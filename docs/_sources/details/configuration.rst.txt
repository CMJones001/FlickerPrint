.. _configuration_values:

Configuration File
==================

The experiment directory contains a ``config.yaml`` file. 
This file contains parameters that can be used to customise the analysis. 
These are divided into sections corresponding to the different stages of the analysis.

Bayesian Paramter Estimation
++++++++++++++++++++++++++++

FlickerPrint contains a Bayesian inference tool to estimate the best imaging parameters to use.
These account for differences in the size, contrast and intensity of the objects of interest.
The tool can be called using

.. code-block:: bash
  
  flickerprint paramter-estimation

from the experiment directory.

The old configuration values are stored in ``old_parameter.txt``.

You can find out more about the Bayesian Inference tool `here <https://doi.org/10.1101/2025.03.24.645013>`_.

Configuration values
++++++++++++++++++++

The available parameters and their default values are given below.

workflow
--------

Parameters used in automating the workflow.
These are not required if the scripts are being run manually, but this is not recommended.

``image_directory``
  Directory containing the image files or the path to a single image file.
  Ideally, this should be given as an absolute path rather than a relative path.

``image_regex``
  **Default:** *\*.ims*

  Glob pattern for microscope images to analyse.
  In the simplest case ``*`` will match any number of characters and ``?`` will match a single character, for example the expression ``*.ims`` will include all files ending in with the ".ims" extension, see `here <http://man7.org/linux/man-pages/man7/glob.7.html>`_ for more details on glob patterns.

``experiment_name``
  Human readable name for the experiments, used in organisation and plotting. Experiments with the same name will be combined by the plotting routines.

image_processing
----------------

Steps used to locate the granule within the image and draw the granule boundary.

``pixel_size``
  **Default:** *0.0*

  The pixel size in microns.
  IMPORTANT: The program will by default try to extract this value from the microscope file's metadata. The value here is only used if the metadata is missing or incomplete. This is especially important for bare image files (ie. .tiff). You will recieve a warning if this value is used. 

``method``
  **Default:** *gradient*

  Method for drawing the boundary, these are:

  * gradient: Find the maximum of the directional gradient (blob)
  * intensity: Find the point at which the intensity crosses a given threshold (wire-frame)

  Different microscopes produce ouput images in different ways; some ouput images as filled in 'blobs' showing instensity, others output a wire-frame image.
  **Typically, gradient is used for condensates while intensity is used for vesicles.**

``Smoothing``
  **Default:** *1.5*

  Noise in the image will often will disrupt the boundary detection. We therefore apply a smoothing to the image to reduce this effect. Too little smoothing will cause poor drawing of the boundary whereas too much will remove detail from the image and suppress higher order modes.
  This is given as a float and represents the Gaussian sigma width.

``granule_minimum_radius``
  **Default:** *0.3*
  
  The minimum radius of a condensate or vesicle, specified in :math:`\mu m`.
  Condensates or vesicles with a radius smaller than this value will be discarded.

``granule_maximum_radius``
  **Default:** *3.0*

  The maximum radius of a condensate or vesicle, specified in :math:`\mu m`.
  Condensates or vesicles with a radius larger than this value will be discarded.

``granule_minimum_intensity``
  **Default:** *0.1*

  The minimum intensity that a granule must have to be detected, relative to the maximum intensity of the image.
  This can be useful when there are brighter granules in the image.

``fill_threshold``
  **Default:** *0.6*

  A flood-fill is used to deterime the approximate size of the granule. 
  This parameter sets the maximum change in intensity between two adjacent pixels for them to be still considered inside the granule.
  This is **not** used to determine the exact location of the boundary.

``granule_images``
  **Default:** *False*

  Save images showing the locations of granules in the microscope image and the boundary of each granule every 100 frames.
  Available options:

  * True
  * False

spectrum_fitting
----------------

Fitting of a theoretical model to the experimentally observed spectrum, to determine the bending regidity and surface tension.

``experimental_spectrum``
  **Default:** *corrected*

  Experimental spectrum used to fit the theoretcial model, required to correct for the likely non-spherical rest shape of the granule.
  Available options:

  * direct - use the magnitude squared of each mode directly
  * corrected - use the standard deviation of the magnitudes

  
``fitting_orders``
  **Default:** *15*

  The maximum order of the fluctuation modes to be used in the spectral fitting.

``temperature``
  **Default:** *37*

  The temperature at which the experiment was conducted in degrees Celsius.

``plot_spectra_and_heatmaps``
  **Default:** *False*

  Save a plot of the fluctuation spectra and heatmaps for each granule (large files which require significant additional processing).
  Available options:

  * True
  * False

Plotting
--------

``latex``
  **Default:** *True*

  Use LaTeX in typsetting on plots.
  Available options:

  * True
  * False

