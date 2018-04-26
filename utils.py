import numpy as np
from skimage import draw

def obtain_hog_image(orientation_histogram, image, N_theta, N_p=5, N_c=3):
    sy, sx = image.shape[:2]
    hog_image = None

    N_x = int(np.floor(sx // N_p))  # number of cells in x
    N_y = int(np.floor(sy // N_p))  # number of cells in y
    radius = N_p // 2 - 1
    hog_image = np.zeros((sy, sx), dtype=float)
    for x in range(N_x):
        for y in range(N_y):
            for o in range(N_theta):
                centre = tuple([y * N_p + N_p // 2, x * N_p + N_p // 2])
                dx = radius * np.cos(float(o) / N_theta * np.pi)
                dy = radius * np.sin(float(o) / N_theta * np.pi)
                rr, cc = draw.line(int(centre[0] - dx),
                                    int(centre[1] - dy),
                                    int(centre[0] + dx),
                                    int(centre[1] + dy))
                hog_image[rr, cc] += orientation_histogram[x, y, o]
    return hog_image