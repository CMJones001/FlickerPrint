.. _getting_started:

===============
Getting started
===============

Creating an experiment
++++++++++++++++++++++

FlickerPrint runs all analysis from an ``experiment directory``.
This contains the experiment's configuration file, where settings can be adjusted, as well as the save locations for all datafiles and figures.
See :ref:`directory_structure` for more details.

Running

.. code-block:: bash

  flickerprint create-project EXPERIMENT_NAME

will create an experiment directory ``EXPERIMENT_NAME`` on disk relative to the current location.
You can then set up set up your experiment by filling out the :ref:`configuration_values` as appropriate.

Configuration File
++++++++++++++++++

The configuration file is where settings for the experiment can be configured.


Most of the default values within the configuration file are sensible defaults. However, the following values should be changed:


``image_directory``
  Directory containing the image files (or the path to a single image file).
  Leaving this as ``default_images`` specifies the ``images`` folder of the experiment sub-directory.

``image_regex``
  `Glob pattern <http://man7.org/linux/man-pages/man7/glob.7.html>`_ for images to include. We currently accept ``.ims``, ``.lif``, ``.ome.tif[f]`` and ``.tif[f]``. With ``.tif[f]`` files, the pixel size must be read from the config file, while in other file types it can be automatically extracted from the metadata.

``experiment_name``
  Human readable name for the experiments, used in organisation and plotting. Experiments with the same name will be combined by the plotting routines.

There are some values in the configuration file which relate to imaging and may need to be adjusted, particularly when analysing images from a new setup.
FlickerPrint includes a Bayesian inference tool to determine the optimal values for these parameters.
It can be called using

.. code-block:: bash

  flickerprint parameter-estimation

See :ref:`configuration_values` for more information about the rest of the parameters in the configuration file.

Running FlickerPrint
++++++++++++++++++++

.. _automatic_workflow:

Automatic workflow
------------------

FlickerPrint's manager handles running the full analysis through the command line, though you can also run parts of the analysis separately or use individual functions from the package if you wish.
The manager is made available to you when you install FlickerPrint.

To use FlickerPrint on the experiment directory you just created, move your terminal into the directory and call

.. code-block:: bash

  flickerprint run

This will analyse all images in the directory you have specified in the config file.
You can optionally add the ``-c CORES`` flag to specify the maximum number of cores that should be used (this is 1 by default).

Manual workflow
---------------

The main workflow of FlickerPrint is split into two main steps: image processing and fluctuation spectrum fitting.

It may not always be preferable to use FlickerPrint's automatic workflow, particularly if you are running analysis in a High Performance Computing (HPC) environment or there are large numbers of condensates in each microscope image.
In these cases, it may make sense to process the micrscope images and fit the fluctuation spectra separately, so that different resources can be allocated to each task.

The two steps are completed using two commands:

.. code-block:: bash

  flickerprint process-image [-i INPUT_IMAGE] [-o OUTPUT_DIR] [-c CORES]

which processes the microscope image(s), at the path ``INPUT_IMAGE`` if it is provided, or those specified in the config file otherwise. The location of each granlue is determined in every frame and its boundary is found.
Next, the fluctuation spectrum must be generated for each granule, allowing the surface tension :math:`\sigma` and the bending rigidity :math:`\kappa` to be determined. To do this, run

.. code-block:: bash

  flickerprint spectrum-fitting WORKING_DIR [-c CORES]

If the working directory is the same as the current directory, ``WORKING_DIR`` can be input as ``.``.
Full details of these steps can be found in the :ref:`workflow` section of the documentation.

Analysing results
+++++++++++++++++

The results from FlickerPrint are stored in the ``aggregate_fittings.h5`` file in the experiment directory. 
All values are standard c-types so you can use your favourite software to filter and analyse the results.
For more information, see :ref:`aggregate_fittings.h5`.

FlickerPrint also contains a Graphical User Interface and associated command-line tools for looking at the output of the analysis.
These can be called using

.. code-block:: bash

  flickerprint view-output

and

.. code-block:: bash

  flickerprint view-output-terminal

respectively.


Version number
++++++++++++++

The version of FlickerPrint which is currently installed can be found using

.. code-block:: bash

  flickerprint version