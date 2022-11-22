from my_py_toolkit.file.file_toolkit import *
import cv2
import numpy as np


def merge_images(files, dim, img_size=None):
    """
    融合图像。

    Args:
        files (list(str)): 文件路径
        dim (int): 融合维度, 0 表示将多图合并为 1 列， 1 表示把多图合并为 1 行
        img_size (list(int), optional): 合并时统一 image size. Defaults to None.

    Returns:
        np.array: 合并后的图像
    """
    imgs = [cv2.imread(f) for f in files]
    if img_size is None:
        img_size = imgs[0].shape[:2]
    imgs = [cv2.resize(img, img_size) for img in imgs]
    imgs =  np.concatenate(imgs, dim)
    return imgs

    
def save_tensor_img(tensor, path='./test.jpg'):
    # 将 torch tensor 还原为图像
    img = tensor.cpu().detach().numpy().transpose(1, 2, 0)
    # img = img * 0.5 + 0.5
    # img *= 255
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite(path, img)