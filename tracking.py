import numpy as np
import cv2

from detection import detection

def tracking(_img1, _img2):
    frame, _, _ = detection(_img1)
    template, _, _ = detection(_img2)
    corr_matr = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF_NORMED)
    
    print(corr_matr)

tracking("img/frame_0060.jpg", "img/frame_0061.jpg")
#cv2.waitKey()