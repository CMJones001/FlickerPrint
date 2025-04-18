.. _granule_detection:

Granule Detection
=================

The first step is to locate the granule within the frame. As these are from microscopy images, we assume that the background of the image will be dark and the granules bright regions.

As the granules are much typically much brighter than the cytoplasm within the cell, a simple thresholding method works will in most cases. However, particularly in the case of transfected cells, the cytoplasm of one cell may be brighter than the granules in another cell, which makes threshold based detection of all the granules impossible.

Therefore, by default this uses the Difference of Gaussian (DoG) method, with the core implementation is provided by `scikit image <https://scikit-image.org/docs/dev/api/skimage.feature.html#skimage.feature.blob_dog>`_.
This is a much more robust method to detect bright granules among a noisy background.

We also provide the Laplacian of Gaussian method, this avoids some of the approximations made in the DoG method and so is better at detecting smaller granules (10s of pixels total area). However, the runtime scales poorly when detecting larger granules and the smaller granules detected by the LoG method are too small for accurate fluctuation analysis, so DoG is typically for that case.

Both the DoG and LoG methods require an estimate of the expected of the granule size to be detected; if the microscope file contains ``PhysicalSize`` of a pixel we choose sensible defaults for stress granules

Implementation
--------------

This provides a ``GranuleDetector_DoG`` class that takes a ``Frame`` object, ``label_granules`` detects the granules within the image and creates a ``mask`` array with 0 for the background and 1 for the granules foreground, ``labelled_granules`` is an array with the same shape of the input image, with a unique image for each granule.
Granules in contact from the boundary are removed.


Source
------

.. automodule:: flickerprint.common.granule_locator
                :members:
                :inherited-members:
