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
    channel: an image array of one channel (H, W)

    Returns
    -------
    I_x: horizontal gradient of the image 
    I_y: vertical gradient of the image
    """
    ####### TODO FUNCTION #######

    I_x, I_y = np.empty_like(channel, dtype=np.float), np.empty_like(channel, dtype=np.float)
    return I_x, I_y
