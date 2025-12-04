import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage
from skimage.filters import try_all_threshold, threshold_otsu
import sklearn.metrics

def detection(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE) #cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
    #cv2.imshow("src", img)

    #m = np.mean(img) # mean
    #x = np.max(img) # max
    #n = np.min(img) # min
    #d = np.std(img) # std
    #delta = x - n # max - min
    #print(m, x, n, d, delta)

    median_filtered = scipy.ndimage.median_filter(img, size=3)
    #cv2.imshow("median_filtered", median_filtered)

    #counts, vals = np.histogram(img, bins=range(2**8))
    #plt.hist(counts, vals)
    #plt.show()

    #result = try_all_threshold(median_filtered)
    #print("try_all_threshold", result)

    threshold = threshold_otsu(median_filtered)
    #print("threshold_otsu", threshold)

    predicted = np.uint8(median_filtered > threshold) * 255
    #cv2.imshow("otsu", predicted)

    return predicted

#detection("img/frame_0012.jpg")

#cv2.waitKey()