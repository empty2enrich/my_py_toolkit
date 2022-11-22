import cv2 as cv
import numpy as np

def resize_resolution(source, target, resolution):
    """
    修改分辨率
    """
    img = cv.imread(source)
    img = cv.resize(img, resolution)
    cv.imwrite(target, img)


def cv_imread(path):
    # 解决 opencv 读取中文路径报错问题
    return cv.imdecode(np.fromfile(path), -1)