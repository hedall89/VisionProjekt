import cv2
import numpy


def centroids(im):
    im_copy = im.copy()
    center_points = []
    if im.dtype == 'float32':
        im_copy = (im_copy*255).astype(numpy.uint8)
    contours, _ = cv2.findContours(im_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        M = cv2.moments(c)
        if M["m00"] != 0:
           center_points.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
        else:
            cX, cY = 0, 0
    return center_points