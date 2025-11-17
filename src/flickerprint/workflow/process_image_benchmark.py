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

    # We need to use multiprocessing even if we're running with only one core due to the javabridge,
    # we need to start the runs as seperate processes.

    process_single_image = partial(
        image_wrapper,
        output_dir=output_dir,
        max_frame=max_frame,
    )

    # args = [(im_path, fft) for im_path, fft in product(image_paths, [True, False])]

    # Works with either True or False hardcoded
    # args = [(im_path, False) for im_path in image_paths]

    # Work's if only True xor False are passed!?!?
    # Even if they're __ignored__
    _args = []
    for im_path in image_paths:
        _args.append((im_path, True))
        _args.append((im_path, False))

    with mp.Pool(processes=n_cores, maxtasksperchild=1) as pool:
        results = pool.map(process_single_image, _args)

    breakpoint()
    results_df = pd.DataFrame(results)
    print(results_df)
    results_df.to_csv("/tmp/results-out.csv")

@fg.vmManager
def image_wrapper(ahhhhhhhh, output_dir: Path, max_frame: Optional[int]):
    """Deal with multiprocessing weirdness and unpack the args before passing it on."""
    # TODO: Slightly insane debugging
    image_path, _use_fft_override = ahhhhhhhh
    use_fft_override = False
    return process_image(image_path=image_path, output_dir=output_dir, max_frame=max_frame, use_fft_override=use_fft_override)

def process_image(
    image_path: Path,
    output_dir: Path,
    max_frame: Optional[int] = None,
    *,
    use_fft_override: Optional[bool] = None,
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

    process_bar = tqdm(
        enumerate(image_frames), unit="frame", total=total_frames, disable=False
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
        "duration_frame": duration/total_frames,
        "fft": use_fft_override,
        "base_name": image_path.stem,
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


if __name__ == "__main__":
    benchmark_path = Path(
        "/home/carl/scratch/postdoc/granule_explorer_project/benchmarks/nikon/out"
    )
    main(input_path=None, output_dir=benchmark_path, max_frame=10)
