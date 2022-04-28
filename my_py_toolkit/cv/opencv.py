

import cv2 as cv

def resize_resolution(source, target, resolution):
    """
    修改分辨率
    """
    img = cv.imread(source)
    img = cv.resize(img, resolution)
    cv.imwrite(target, img)

