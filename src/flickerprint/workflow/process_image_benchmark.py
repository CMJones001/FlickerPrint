"""
Benchmarkable version of the ``process_image.py`` script.
=========================================================

This is a single core version for simplicity.
"""

import multiprocessing as mp
from dataclasses import dataclass
from functools import partial
from itertools import chain, islice, product
from pathlib import Path
from time import perf_counter
from typing import Optional
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from more_itertools import peekable
from tqdm import tqdm

import flickerprint.common.boundary_extraction as be
import flickerprint.common.frame_gen as fg
import flickerprint.common.granule_locator as gl
import flickerprint.common.granule_locator_fft as glf
import flickerprint.tools.plot_tools as pt
import flickerprint.workflow.process_image as pi
from flickerprint.common.configuration import config
from flickerprint.common.utilities import strtobool


def main(
    input_path: Optional[Path],
    output_dir: Path,
    n_cores: int = 1,
    max_frame: Optional[int] = None,
):
    config_path = output_dir / "config.yaml"
    config.refresh(config_path)

    image_paths = parse_input_images(input_path, output_dir)

    if n_cores != 1:
        # This should work just as well when running with one core, but there's some madness going on
        process_single_image = partial(
            image_wrapper,
            output_dir=output_dir,
            max_frame=max_frame,
        )

        args = [
            (im_path, fft, pos)
            for pos, (im_path, fft) in enumerate(product(image_paths, [True, False]))
        ]
        with mp.Pool(processes=n_cores, maxtasksperchild=1) as pool:
            results = pool.starmap(process_single_image, args)

        results_df = pd.DataFrame(results)
    else:
        results_df = run_serial(image_paths, output_dir, max_frame)

    print(results_df)
    results_df.to_csv("/tmp/results-out.csv")


@fg.vmManager
def run_serial(image_paths: Path, output_dir: Path, max_frame: Optional[int]):
    results = []
    for im_path, fft in product(image_paths, [True, False]):
        result_part = process_image(
            image_path=im_path,
            output_dir=output_dir,
            max_frame=max_frame,
            use_fft_override=fft,
        )
        results.append(result_part)

    results_df = pd.DataFrame(results)
    return results_df


@fg.vmManager
def image_wrapper(image_path, fft, bar_pos, output_dir: Path, max_frame: Optional[int]):
    """Deal with multiprocessing weirdness and unpack the args before passing it on.

    This also means that we can have a seperate ``vmManager`` entry point from the serial version.

    I have no earthly idea what is going on when this is run with one core enabled. There is an
    error that the VM cannot be started.

    ```
    _args = []
    for im_path in image_paths:
        _args.append((im_path, True, output_dir, max_frame))
        _args.append((im_path, False, output_dir, max_frame))
    ```

    works _if and only if_ one of the append lines is commented out. This error persists even if
    this wrapper ignores the arguments and just `sleeps`. It persists when using the `pool.map`
    version and they're a tuple. It persists when I replace True/False with `a`/`b`. It persists
    with or without using ``partial``. But remove one of the lines and it's fine...

    """
    return process_image(
        image_path=image_path,
        output_dir=output_dir,
        max_frame=max_frame,
        use_fft_override=fft,
        _bar_pos=bar_pos,
    )


def process_image(
    image_path: Path,
    output_dir: Path,
    max_frame: Optional[int] = None,
    *,
    use_fft_override: Optional[bool] = None,
    _bar_pos: Optional[int] = None,
):
    start_time = perf_counter()
    config_path = output_dir / "config.yaml"
    config.refresh(config_path)

    image_frames = peekable(fg.gen_opener(image_path))
    frame = image_frames.peek()
    n_frames = frame.total_frames

    if use_fft_override:
        blurrer = pi._get_blurrer(frame)
        detector_function = partial(glf.GranuleDetectorFFT, blurrer=blurrer)
    else:
        detector_function = gl.GranuleDetector

    fourier_frames = []
    max_distance = float(config("image_processing", "tracking_threshold"))
    granule_tracker = be._GranuleLinker(memory=10, max_distance=max_distance)

    if max_frame is not None:
        total_frames = min(n_frames, max_frame)
        image_frames = islice(image_frames, max_frame)
    else:
        total_frames = n_frames

    if _bar_pos is not None:
        description = f"#{_bar_pos+1}"
    else:
        description = None

    process_bar = tqdm(
        enumerate(image_frames),
        unit="frame",
        total=total_frames,
        disable=False,
        position=_bar_pos,
        desc=description,
    )

    label = "_fft" if use_fft_override else "_base"
    save_dirs = SaveDirs(output_dir, ext=label)
    save_dirs.create_dirs()

    for frame_num, frame in process_bar:

        if bool(strtobool(config("image_processing", "granule_images"))):
            plot_frames = frame_num % 100 == 0
        else:
            plot_frames = False
        plot_granules = False

        detector = detector_function(frame)
        try:
            detector.labelGranules()
        except gl.GranuleNotFoundError:
            if frame_num == 0:
                print("No granules found on first frame, quitting")
                process_bar.close()
                raise gl.GranuleNotFoundError(
                    f"No granules found in {image_path}. Please check the values in the config file and try again."
                )
            else:
                continue

        if plot_frames:
            plot_save_path = (
                save_dirs.detection_dir / f"{image_path.stem}--F{frame_num:03d}.png"
            )
            _create_detection_plots(detector, frame, save_path=plot_save_path)

        boundary_method = config("image_processing", "method")
        try:
            granule_boundries = [
                be.BoundaryExtraction(granule, boundary_method)
                for granule in detector.granules()
            ]
        except gl.GranuleNotFoundError:
            continue

        # Tidy these Fourier terms per frame
        # This is an iterative function that reuses results from the previous frames.
        try:
            aggregate_terms = be.collect_fourier_terms(
                granule_boundries, frame, granule_tracker, plot_granules, output_dir
            )
            fourier_frames.append(aggregate_terms)
        except gl.GranuleNotFoundError:
            continue

    fourier_frames_df = pd.concat(fourier_frames, ignore_index=True)
    df_save_path = save_dirs.fourier_dir / f"{image_path.stem}.h5"

    frame_data = {
        "num_frames": total_frames,
        "input_path": str(image_path.resolve()),
        "pixel_size": frame.pixel_size,
    }

    pi.write_hdf(df_save_path, fourier_frames_df, frame_data)
    end_time = perf_counter()
    duration = end_time - start_time

    props = {
        "duration_total": duration,
        "n_frames": total_frames,
        "duration_frame": duration / total_frames,
        "fft": use_fft_override,
        "base_name": image_path.stem,
        "version_np": np.__version__,
    }

    return props


def _create_detection_plots(detector, frame, save_path: Path):
    cmap = plt.get_cmap("tab20")
    cmap.set_bad((0, 0, 0, 0))
    fig, axs = pt.create_axes(2)

    masked_granules = np.ma.masked_equal(detector.labelled_granules, 0)
    axs[0].imshow(masked_granules, cmap=cmap, interpolation="none")
    axs[1].imshow(
        frame.im_data,
        cmap="inferno",
    )

    axis_len = max(frame.im_data.shape)
    tick_spacing = 256 if axis_len > 2000 else 128

    titles = ["Detected", "Original"]

    for ax, title in zip(axs, titles):
        ax.set_title(title)
        ticks = np.arange(0, axis_len + 1, step=tick_spacing)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)

    pt.save_figure_and_trim(save_path, dpi=330)


def parse_input_images(input_path: Optional[Path], output_dir: Path) -> list[Path]:
    """Return a list of the images to process"""
    # Fall back to the configuration file if nothing is provided
    if input_path is None:
        input_path = str(config("workflow", "image_dir"))
        if input_path == "":
            raise SystemExit(
                "No input image provided and no directory set in the configuration file"
            )

        input_path = Path(input_path)
        if not input_path.is_absolute():
            input_path = (output_dir / input_path).resolve()

    # If the path is file, then we're done
    input_path = Path(input_path)
    if input_path.is_file():
        return [input_path]
    if not input_path.is_dir():
        raise SystemExit(f"input_path {input_path} is neither a file or directory.")

    # We're left with directories, so scan for these for files
    image_regexes = [str(config("workflow", "image_regex"))]
    file_paths = list(
        chain.from_iterable((input_path.glob(regex) for regex in image_regexes))
    )

    if len(file_paths) == 0:
        raise SystemExit("No files found in {image_path}")
    return file_paths


@dataclass
class SaveDirs:
    base_dir: Path
    ext: Optional[Path] = None

    @property
    def plot_dir(self) -> Path:
        # I can't remember if f"{None}" is empty or just "None", if it's the former, then these are
        # redundant.
        if self.ext is None:
            return self.base_dir / "tracking"
        else:
            return self.base_dir / f"tracking{self.ext}"

    @property
    def detection_dir(self) -> Path:
        return self.plot_dir / "detection"

    @property
    def fourier_dir(self) -> Path:
        if self.ext is None:
            return self.base_dir / "fourier"
        else:
            return self.base_dir / f"fourier{self.ext}"

    def create_dirs(self):
        self.plot_dir.mkdir(exist_ok=True)
        self.detection_dir.mkdir(exist_ok=True)
        self.fourier_dir.mkdir(exist_ok=True)

def parse_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--input", type=Path, help="Path to input image or directory of input images.", default=None)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=".",
        help="Directory for the output files.",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Supress progress bar."
    )

    parser.add_argument(
        "--max-frame",
        type=int,
        default=None,
        help="Stop the analysis on this frame. Used for debugging.",
    )

    parser.add_argument(
        "-c","--cores",
        type=int,
        default=1,
        help="Number of cores to use for multiprocessing. Default is 1. Not required for single files.")

    args = parser.parse_args()
    return args




if __name__ == "__main__":
    benchmark_path = Path(
        "/home/carl/scratch/postdoc/granule_explorer_project/benchmarks/nikon/out"
    )
    main(input_path=None, output_dir=benchmark_path, max_frame=10, n_cores=1)
