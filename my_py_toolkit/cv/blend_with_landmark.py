#  使用 landmarks 获取 mask, 进行人脸合成

import albumentations as A
import cv2
import numpy as np
from PIL import Image





########################################### self blend image

def draw_convex_hull(img, points, color):
    hull = cv2.convexHull(points)
    cv2.fillConvexPoly(img, hull, color=color)
    
def get_landmark(img, detector, predictor):
    faces = detector(img, 1)
    shape = predictor(img, faces[0]).parts()
    return np.matrix([[p.x, p.y] for p in shape])

def get_mask(img, landmarks, mask_trans):
    # landmarks = get_landmark(img)
    mask = np.zeros(img.shape[:2])
    draw_convex_hull(mask, landmarks, 1)
    mask = np.array([mask]*3).transpose(1, 2, 0)
    mask = mask_trans(image=mask)['image']
    # todo : 高斯核后续测试小不同参数
    mask = (cv2.GaussianBlur(mask, (11, 11), 0) > 0) * 1.0
    mask = cv2.GaussianBlur(mask, (11, 11), 0)
    return mask


def get_trans(h, w, crop_scale):
    mask_trans = A.Compose([
        A.RandomResizedCrop(h, w, crop_scale),
        A.ElasticTransform()
        ])

    trans = [
        A.RGBShift(),
        A.HueSaturationValue(),
        A.RandomBrightness(),
        A.ColorJitter(),
        A.Downscale(0.9, 0.9),
        A.Sharpen(),
        A.RandomResizedCrop(h, w, crop_scale)
    ]
    return trans, mask_trans


def get_raito():
    raitos = [0.25, 0.5, 0.75, 1, 1, 1]
    idx = np.random.randint(0, 6)
    return raitos[idx]


def self_blend(img, landmarks, trans, mask_trans):
    source = img.copy()
    target = img.copy()
    mask = get_mask(img, landmarks, mask_trans)
    raito = get_raito()
    for tf in trans:
        if np.random.random() > 0.5:
            source = tf(image=source)['image']
        else:
            target = tf(image=target)['image']
    # todo: 后续试试没有 mask * （1 - raito） 效果
    mask = mask * (1 - raito)
    img_tf = source * (1 - mask) + target * mask
    return img_tf
    