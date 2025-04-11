.. _directory_structure:

Structure of the Experiment Directory
=====================================

FlickerPrint runs all analysis from an ``experiment directory``.
This contains the experiment's configuration file, where settings can be adjusted as well as the save locations for all datafiles and figures.

A number of sub-directories and files created to organise the output of the analysis:

**aggregate_fittings.h5**
   The location of the final results of the analysis, containing the measured interfacial tension and bending rigidity for all objects.

   See :ref:`data_storage` for details on the structure of the files.

**figs/**
    Directory for figures showing the final parameter distributions from the analysis.

**fitting/**
    Optional figures showing the fitting of the theoretical model to the experimental spectrum. This can be used to inspect the individual fitting quality for each object.

**fourier/**
   A directory for the first stage of the results, containing the location of the objects of interest within the frame and the amplitude of their fourier modes in each frame.

   See :ref:`data_storage` for the structure of the files.

**images/**
    A directory for the raw microscope files for the analysis. If the microscope files are stored in a different location, this should be specified in the :ref:`configuration_values`.

**tracking/**
    Optional figures showing the detection of the granules within the image and the boundary drawing around individual granules.
    In order to save on disk space, figures are only recorded every 100 frames.

