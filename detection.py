import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage
from skimage.filters import try_all_threshold, threshold_otsu
import sklearn.metrics

def detection(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE) 
    #img = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_GRAYSCALE)
    median_filtered = scipy.ndimage.median_filter(img, size=3)
    threshold = threshold_otsu(median_filtered)
    predicted = np.uint8(median_filtered > threshold) * 255
    _, thresh = cv2.threshold(img, threshold + 10, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(contours, key=cv2.contourArea)

    #x, y, w, h = cv2.boundingRect(cnt)
    #print("Bounding box:")
    #print("x_min =", x, "y_min =", y)
    #print("x_max =", x + w, "y_max =", y + h)

    M = cv2.moments(cnt)
    #cx = int(M["m10"] / M["m00"])
    #cy = int(M["m01"] / M["m00"])
    #print("Centroid:", cx, cy)

    #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #cv2.imshow("result", img)
    return predicted, cnt, M

#detection("img/frame_0045.jpg")
#cv2.waitKey(0)