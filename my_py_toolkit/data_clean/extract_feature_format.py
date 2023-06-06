# -*- coding: utf-8 -*-
"""
Created on 18-5-30 下午4:55

@author: ronghuaiyang
"""
from __future__ import print_function
import os
import cv2
import torch
import numpy as np
import time
from my_py_toolkit.file.file_toolkit import *
from tqdm import tqdm
import traceback

# import model, load image fun, get_images_fn
# from local import model, load_image, get_images

def load_image(img_path):
    image = cv2.imread(img_path, 0)
    if image is None:
        return None
    image = cv2.resize(image, (128, 128))
    image = np.dstack((image, np.fliplr(image)))
    image = image.transpose((2, 0, 1))
    image = image[:, np.newaxis, :, :]
    image = image.astype(np.float32, copy=False)
    image -= 127.5
    image /= 127.5
    return image

def write_embedding(files, features, writer):
    features = features.tolist()
    for file, feature in zip(files, features):
        feature = ','.join([str(v) for v in feature])
        writer.write(f'{file} {feature}\n')

def get_featurs(model, test_list, batch_size=10, device='cuda', save_path='embedding.txt'):
    images = None
    features = None
    cnt = 0
    cur_image_paths = []
    writer = open(save_path, 'a+', encoding='utf-8')
    for i, img_path in tqdm(enumerate(test_list)):
        try:
            image = load_image(img_path)
            if image is None:
                print('read {} error'.format(img_path))
                continue

            cur_image_paths.append(img_path)

            if images is None:
                images = image
            else:
                images = np.concatenate((images, image), axis=0)

            if images.shape[0] % batch_size == 0 or i == len(test_list) - 1:
                cnt += 1

                data = torch.from_numpy(images)
                data = data.to(device)
                output = model(data)
                feature = output.data.cpu().numpy()

                write_embedding(cur_image_paths, feature, writer)


                if features is None:
                    features = feature
                else:
                    features = np.vstack((features, feature))

                images = None
                cur_image_paths = []
        except:
            print('read {} error'.format(img_path))
            print()

    return features, cnt


def get_feature_dict(test_list, features):
    fe_dict = {}
    for i, each in enumerate(test_list):
        # key = each.split('/')[1]
        fe_dict[each] = features[i]
    return fe_dict


def cosin_metric(x1, x2):
    return np.dot(x1, x2) / (np.linalg.norm(x1) * np.linalg.norm(x2))



if __name__ == '__main__':
    device = 'cuda'
    save_path = 'recce_trainset_features.txt'
    batch_size = 600
    model = model
    files = get_images()

    # files = ['checkpoints/lfw-align-128/Eve_Ensler/Eve_Ensler_0001.jpg']
    features, cnt = get_featurs(model, files, batch_size, device, save_path)
    print(features.shape)
    print(features)




