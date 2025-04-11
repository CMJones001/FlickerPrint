.. _data_storage:

Data Storage
============

During the analysis we make use of `hdf5 <https://www.hdfgroup.org/solutions/hdf5/>`_ files to store data. These are faster to access than ``csv`` or similar text files, while being much more space efficient. 
Importantly, they allow for lossless storage of data while retaining the correct data format (dates or complex numbers are particularly troublesome in csv) and for storage of multiple tables that allows storage of secondary data in a much cleaner manner.

Bindings exist for most major programming languages or with the standalone `HDFView <https://www.hdfgroup.org/downloads/hdfview/>`_ software.

.. _fourier.h5:

fourier.h5
----------

These intermediary files contain the locations of the objects of interest within the microscope files and the Fourier components of their boundaries. 
The files are created by the :ref:`image processing <image_processing>` stage of FlickerPrint, with one file produced per microscope file.

This file is split into two components:

* :ref:`fourier`
   * :ref:`Attributes <fourier_attributes>`

.. _fourier:

fourier
+++++++++++++

Primarily contains a `pandas.DataFrame` (table) with the headers:

:im_path:
   **str**

   The path of the microscope image used for the analysis

:frame:
   **int**

   The frame number for which we record the data

:granule_id:
   **int**

   Each granule is assigned an ID as it is tracked across the frames

:order:
   **int**

   Fluctuation order, ``q``

:magnitude:
   **float_complex**

   Complex magnitude of the given mode ``q`` for this granule

.. :order_1:
..    **float_complex**

..    The Complex magnitude of the first mode for this granule. This determines the location of the granule center only

:x, y:
   **float**, **float**

   Position of the granule centre in pixel coordinates

:bbox_left, bbox_bottom, bbox_right, bbox_top:
   **float**, **float**, **float**, **float**

   Positions of the corners of the box bounding the granule

:mean_radius:
   **float**

   Radius of the granule

:valid:
   **bool**

   If ``False`` then a discontinuity has been detected in the boundary drawing for this frame

:major_axis:
   **float**

   Fit an ellipse to the granule and measure the major axis of the in pixels

:eccentricty:
   **float**

   Fit an ellipse to the granule and measure the eccentricty

:timestamp:
   **str**

   The date and time that this frame was taken, if available. Otherwise zero

.. _fourier_attributes:

Attributes
++++++++++

These data are attached to the ``fourier`` table as attributes to provide further information:

:num_frames:
   **int**

   The total number of frames in the microscope image file

:input_path:
   **str**

   The path of the file used in the analysis

:pixel_size:
   **float**

   The physical size on the sample of a pixel in the image (μm/pixel)

:config:
   **str**

   A copy of the config file used to run the "process-image" step that produced this file
   
:version:
   **str**

   The version number of the Granule Explorer code that produced this file

.. _aggregate_fittings.h5:

aggregate_fittings.h5
---------------------

The aggregate fittings file is the final output of the main FlickerPrint workflow.
This file contains tables listing the granule properties and fitting information. One file is produced per experiment directory.

This is split into three components:

* :ref:`aggregate_data`
   * :ref:`aggregate_data_attributes`
* :ref:`fourier_terms`

.. _aggregate_data:

aggregate_data
++++++++++++++

A ``pandas.DataFrame`` containing a list of granule properties, with the columns:

:granule_id:
   **int**

   Each granule is assigned an ID during the image processing step, note that this is only unique when combined with the ``image_path``.

:sigma:
   **float**

   Best fit surface tension for the granule in units of N/m

:sigma_err:
   **float**

   The estimated error of sigma in N/m

:kappa_scale:
   **float**

   Best fit bending rigidity for the granule, measured in units of k :sub:`B` T

:kappa_scale_err:
   **float**

   The estimated error of kappa in k :sub:`B` T

:mean_radius:
   **float**

   Mean radius of the granule in μm

:figure_path:
   **str**

   The name of the spectrum fitting figure produced by the analysis.

:image_path:
   **str**

   The name of the file used to create the granule information in the image processing step

:pass_rate:
   **float**

   The percentage of frames that have valid boundaries drawn ``image-processing``, used to exclude the granule if too many frames fail

:pass_count:
   **int**

   The number of frames in which this this granule appears and has a valid boundary drawn in ``image-processing``. Used to exclude the granule if it only appears in a few frames

:fitting_error:
   **float**

   The fitting error between the experimental fluctuation spectrum and the theoretical spectrum

:durbin_watson:
   **float**

   The Durbin-Watson statistic for the spectrum (a measure of correlation between residuals of adjacent Fourier modes), used to determine whether a model is a good fit to the data. See `here <https://en.wikipedia.org/wiki/Durbin–Watson_statistic>`_ for details.

:mean_intensity: 
   **float**

   The mean intensity of pixels belonging to the granule (arb units)

:x, y:
   **float** , **float**

   Position of the granule centre in pixel coordinates

:bbox_left, bbox_bottom, bbox_right, bbox_top:
   **float**, **float**, **float**, **float**

   Positions of the corners of the box bounding the granule

:q_2_mag:
   **float**

   The average magnitude of the second fluctuation mode. Gives an estimate of the circularity of the granule

:experiment:
   **str**
   
   A string name of the experiment, used to combine seperate files from the same experiment, or compare different experiments

:timestamp:
   **str**

   A the date and time that the granule first appears in the microscope file   

:fitting_diff:
   **float**

   The difference in fitting error between models which include interfacial tension only and both interfacial tension and bending rigidity

:sigma_st:
   **float**
   The interfacial tension as measured using the interfacial tension only model.

:sigma_err_st:
   **float**

   The error on interfacial tension when using the interfacial tension only model.

.. _aggregate_data_attributes:

Attributes
++++++++++

The ``aggregate_data`` frame has the following attributes:

:config:
   **str**

   A copy of the config file used to run the "spectrum-fitting" step.

:version:
   **str**

   The version number of the Granule Explorer code that produced this file.

.. _fourier_terms:

fourier_terms
+++++++++++++


A second frame containing spectrum information for each object. This contains the following columns:

:order:
   **int**

   The peturbation order, ``q``.

:mag_squ_mean:
   **float**

   The total perturbations from a circular granule: the mean of the absolute magnitude squared

:mag_mean:
   **float_complex**

   The mean of the complex perturbations across the surface.

:fixed_squ:
   **float**

   The squared magnitude of the static components.

:fluct_squ:
   **float**

   The squared magnitude of the fluctuating components on top of the quasi-spherical static shape.

:experimental_spectrum:
   **float**

   The spectrum used in fitting, it is typically ``fluct_squ`` unless set otherwise by the configuration file.

:best-fit:
   **float**

   The best fit theoretical spectrum to the ``experimental_spectrum``

:granule_id:
   **int**

   Each granule is assigned an ID during the image processing step, note that this is only unique when combined with the ``figure_path``.

:figure_path:
   **str**

   Output figure path
