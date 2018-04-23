import numpy as np
import matplotlib.pyplot as plt
from skimage import data, exposure
from skimage.color import rgb2gray
from scipy import sqrt, pi, arctan2, cos, sin
from scipy.ndimage import uniform_filter


def hog(image, N_theta=9, N_p=5,
        N_c=3, visualise=False):
    """Extract Histogram of Oriented Gradients (HOG) for a given image.

    Compute a Histogram of Oriented Gradients (HOG) by

        1. (optional) global image normalisation
        2. computing the gradient image in x and y
        3. computing gradient histograms
        4. normalising across blocks
        5. flattening into a feature vector

    Parameters
    ----------
    image : (M, N) ndarray
        Input image (greyscale).
    N_theta : int
        Number of orientation bins.
    N_p : int
        Size (in pixels) of a cell.
    N_c  : 2 tuple (int,int)
        Number of cells in each block.
    visualise : bool, optional
        Also return an image of the HOG.

    Returns
    -------
    newarr : ndarray
        HOG for the image as a 1D (flattened) array.
    hog_image : ndarray (if visualise=True)
        A visualisation of the HOG image.

    References
    ----------
    * http://en.wikipedia.org/wiki/Histogram_of_oriented_gradients

    * Dalal, N and Triggs, B, Histograms of Oriented Gradients for
      Human Detection, IEEE Computer Society Conference on Computer
      Vision and Pattern Recognition 2005 San Diego, CA, USA

    """
    image = np.atleast_2d(image)

    """
    The first stage applies an optional global image normalisation
    equalisation that is designed to reduce the influence of illumination
    effects. In practice we use gamma (power law) compression, either
    computing the square root or the log of each colour channel.
    Image texture strength is typically proportional to the local surface
    illumination so this compression helps to reduce the effects of local
    shadowing and illumination variations.
    """

    if image.ndim > 2:
        raise ValueError("Currently only supports grey-level images")

    """
    The second stage computes first order image gradients. These capture
    contour, silhouette and some texture information, while providing
    further resistance to illumination variations. The locally dominant
    colour channel is used, which provides colour invariance to a large
    extent. Variant methods may also include second order image derivatives,
    which act as primitive bar detectors - a useful feature for capturing,
    e.g. bar like structures in bicycles and limbs in humans.
    """

    if image.dtype.kind == 'u':
        # convert uint image to float
        # to avoid problems with subtracting unsigned numbers in np.diff()
        image = image.astype('float')

    gx = np.zeros(image.shape)
    gy = np.zeros(image.shape)
    gx[:, :-1] = np.diff(image, n=1, axis=1)
    gy[:-1, :] = np.diff(image, n=1, axis=0)

    """
    The third stage aims to produce an encoding that is sensitive to
    local image content while remaining resistant to small changes in
    pose or appearance. The adopted method pools gradient orientation
    information locally in the same way as the SIFT [Lowe 2004]
    feature. The image window is divided into small spatial regions,
    called "cells". For each cell we accumulate a local 1-D histogram
    of gradient or edge N_theta over all the pixels in the
    cell. This combined cell-level 1-D histogram forms the basic
    "orientation histogram" representation. Each orientation histogram
    divides the gradient angle range into a fixed number of
    predetermined bins. The gradient magnitudes of the pixels in the
    cell are used to vote into the orientation histogram.
    """

    magnitude = sqrt(gx**2 + gy**2) # TODO
    orientation = arctan2(gy, gx + 1e-15) * (180 / pi) % 180

    sy, sx = image.shape
    cx, cy = N_p, N_p
    bx, by = N_c, N_c

    n_cellsx = int(np.floor(sx // cx))  # number of cells in x
    n_cellsy = int(np.floor(sy // cy))  # number of cells in y

    # compute N_theta integral images
    orientation_histogram = np.zeros((n_cellsy, n_cellsx, N_theta))
    subsample = np.index_exp[cy // 2:cy * n_cellsy:cy,
                             cx // 2:cx * n_cellsx:cx]
    for i in range(N_theta):
        # create new integral image for this orientation
        # isolate N_theta in this range

        temp_ori = np.where(orientation < 180.0 / N_theta * (i + 1),
                            orientation, -1)
        temp_ori = np.where(orientation >= 180.0 / N_theta * i,
                            temp_ori, -1)
        # select magnitudes for those N_theta
        cond2 = temp_ori > -1
        temp_mag = np.where(cond2, magnitude, 0)

        temp_filt = uniform_filter(temp_mag, size=(cy, cx))
        orientation_histogram[:, :, i] = temp_filt[subsample]

    # now for each cell, compute the histogram
    hog_image = None

    if visualise:
        from skimage import draw

        radius = min(cx, cy) // 2 - 1
        hog_image = np.zeros((sy, sx), dtype=float)
        for x in range(n_cellsx):
            for y in range(n_cellsy):
                for o in range(N_theta):
                    centre = tuple([y * cy + cy // 2, x * cx + cx // 2])
                    dx = radius * cos(float(o) / N_theta * np.pi)
                    dy = radius * sin(float(o) / N_theta * np.pi)
                    rr, cc = draw.line(int(centre[0] - dx),
                                       int(centre[1] - dy),
                                       int(centre[0] + dx),
                                       int(centre[1] + dy))
                    hog_image[rr, cc] += orientation_histogram[y, x, o]

    """
    The fourth stage computes normalisation, which takes local groups of
    cells and contrast normalises their overall responses before passing
    to next stage. Normalisation introduces better invariance to illumination,
    shadowing, and edge contrast. It is performed by accumulating a measure
    of local histogram "energy" over local groups of cells that we call
    "blocks". The result is used to normalise each cell in the block.
    Typically each individual cell is shared between several blocks, but
    its normalisations are block dependent and thus different. The cell
    thus appears several times in the final output vector with different
    normalisations. This may seem redundant but it improves the performance.
    We refer to the normalised block descriptors as Histogram of Oriented
    Gradient (HOG) descriptors.
    """

    n_blocksx = (n_cellsx - bx) + 1
    n_blocksy = (n_cellsy - by) + 1
    normalised_blocks = np.zeros((n_blocksy, n_blocksx,
                                  by, bx, N_theta))

    for x in range(n_blocksx):
        for y in range(n_blocksy):
            block = orientation_histogram[y:y + by, x:x + bx, :]
            eps = 1e-5
            normalised_blocks[y, x, :] = block / sqrt(block.sum()**2 + eps) # TODO

    """
    The final step collects the HOG descriptors from all blocks of a dense
    overlapping grid of blocks covering the detection window into a combined
    feature vector for use in the window classifier.
    """

    if visualise:
        return normalised_blocks.ravel(), hog_image
    else:
        return normalised_blocks.ravel()


if __name__ == "__main__":
    # img = rgb2gray(data.lena())
    img = rgb2gray(data.astronaut())


    fd, hog_img = hog(img, N_theta=9, N_p=5, N_c=3, visualise=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)

    ax1.axis('off')
    ax1.imshow(img, cmap=plt.cm.gray)
    ax1.set_title('Input image')

    # Rescale histogram for better display
    hog_image_rescaled = exposure.rescale_intensity(hog_img, in_range=(0, 10))

    ax2.axis('off')
    ax2.imshow(hog_image_rescaled, cmap=plt.cm.gray)
    ax2.set_title('Histogram of Oriented Gradients')
    plt.show()