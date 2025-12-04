import numpy as np
import cv2

from detection import detection

def tracking(_img1, _img2):
    img1 = detection(_img1)
    img2 = detection(_img2)

    m1 = np.mean(img1)
    m2 = np.mean(img2)

    std1 = np.std(img1)
    std2 = np.std(img2)

    r = t = x = y = 0

    height1, width1 = img1.shape
    height2, width2 = img2.shape

    height = int(max(height1, height2))
    width = int(max(width1, width2))

    for i in img1:
        for j in img1:
            t += img1[i][j] * img2[i][j]
            x += np.sqrt(np.pow(img1[i][j], 2))
            y += np.sqrt(np.pow(img2[i][j], 2))

    r = t / (x * y)

    return r


#print(tracking("img/frame_0011.jpg", "img/frame_0012.jpg"))