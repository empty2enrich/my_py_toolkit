import imp
import cv2
import dlib
import math
import numpy as np
import os

from my_py_toolkit.file.file_toolkit import *

def single_face_alignment(face, landmarks):
    eye_center = ((landmarks[36, 0] + landmarks[45, 0]) * 1. / 2,  # 计算两眼的中心坐标
                  (landmarks[36, 1] + landmarks[45, 1]) * 1. / 2)
    dx = (landmarks[45, 0] - landmarks[36, 0])  # note: right - right
    dy = (landmarks[45, 1] - landmarks[36, 1])

    angle = math.atan2(dy, dx) * 180. / math.pi  # 计算角度
    RotateMatrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1)  # 计算仿射矩阵
    align_face = cv2.warpAffine(face, RotateMatrix, (face.shape[0], face.shape[1]))  # 进行放射变换，即旋转
    return align_face

def get_landmark(img, detector, predictor):
    # dlib_path = './models/shape_predictor_81_face_landmarks.dat'
    # detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor(dlib_path)
    faces = detector(img, 1)
    if len(faces) > 0:
        shape = predictor(img, faces[0]).parts()
        return np.matrix([[p.x, p.y] for p in shape])
    else:
        return None
    
def face_align(path, save_dir):
    img = cv2.imread(path)
    landmarks = get_landmark(img)
    face_ali = single_face_alignment(img, landmarks)
    
    save_path = os.path.join(save_dir, get_file_name(path))
    make_path_legal(save_path)
    cv2.imwrite(save_path, face_ali)
    
    
if __name__ == '__main__':
    p = 'test_imgs/1.jpg'
    img = cv2.imread(p)
    landmarks = get_landmark(img)
    face_ali = single_face_alignment(img, landmarks)