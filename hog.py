import numpy as np
from PIL import Image
from typing import Tuple


def _normalize_block(block: np.ndarray, eps: float=1e-5) -> np.ndarray:
    """
    Normalize the features in block.

    Parameters
    ----------
    block: an area of the image which consists of a certain size of cells
    eps: a small real number

    Returns
    -------
    normalized_block: normalized block
    """
    ####### TODO FUNCTION #######

    normalized_block = np.empty_like(block)
    return normalized_block


def _compute_gradient(channel: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute gradients both vertically and horizontally.

    Parameters
    ----------
    channel: an image array of one channel (W, H)

    Returns
    -------
    I_x: horizontal gradient of the image 
    I_y: vertical gradient of the image
    """
    ####### TODO FUNCTION #######

    I_x, I_y = np.empty_like(channel, dtype=np.float), np.empty_like(channel, dtype=np.float)
    return I_x, I_y


def calculate_hog(image: np.ndarray, N_theta: int=9, N_p: int=5, N_c: int=3) -> np.ndarray:
    """
    Compute HOG feature from image.

    Parameters
    ----------
    image: an image array. the dimension is either (W, H) or (W, H, C)
    N_theta: the number of bins of angle
    N_p: the grid size of pixels in a cell
    N_c: the grid size of cells in a block

    Returns
    -------
    hog: the hog feature extracted from image. the dimension is (N_theta * N_c * N_c) * (size_w - N_c + 1) * (size_h - N_c + 1)
    """
    ####### TODO FUNCTION #######

    size_w, size_h = image.shape[:2]
    dim_hog = (N_theta * N_c * N_c) * (size_w - N_c + 1) * (size_h - N_c + 1)
    hog = np.empty(dim_hog)
    return hog
