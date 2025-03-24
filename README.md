# FlickerPrint

FlickerPrint is a software package for conducting flicker spectroscopy analysis to find the interfacial tension and bending rigidity of soft bodies such as biomolecular condensates and vesicles from their shape fluctuations in confocal microscopy images.

## Prerequisites

FlickerPrint requires Python 3.9 to 3.11 and an installation of Java.
Full details of how to install these prerequisies will be available in the documentation.

## Installation

Installation of FlickerPrint directly via pip is not yet supported. To install the package, clone the Git repository, then navigate to the root directory of the repository and run:

```bash
pip install -e .
```

## Usage

FlickerPrint is primarily used through the command line. To see the available commands and options, run:

```bash
flickerprint --help
```

To create a new experiment, run:

```bash
flickerprint create-project <project_name>
```

To analyse a dataset, ``cd`` into the experiment directory and run:

```bash
flickerprint run [-c cores]
```