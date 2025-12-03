import cv2
import numpy as np


def detection(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE) #cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)

    m = np.mean(img) # mean
    x = np.max(img) # max
    n = np.min(img) # min
    d = np.std(img) # std

    delta = x - n

    print(m, x, n, d, delta)