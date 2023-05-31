import sys
from tabnanny import check
import cv2
import numpy as np
import re
import PIL.Image as Image
import numpy as np
import configparser
from shutil import copy, move
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
from my_py_toolkit.file.file_toolkit import *
import argparse
from tqdm import tqdm


f = open('./log.txt', 'a+')
sys.stdout = f

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, help='data dir or filelist')  # allows running as root; implemented outside of webui
    parser.add_argument("--ori_dir", type=str, help='data dir')  # allows running as root; implemented outside of webui
    parser.add_argument("--save_dir", type=str, help='save_dir')  # allows running as root; implemented outside of webui
    parser.add_argument("--gen_nums", type=int, help='gen_nums')  # allows running as root; implemented outside of webui
    parser.add_argument("--suffix", type=str, default='bmp', help='suffix')  # allows running as root; implemented outside of webui
    return parser.parse_args()




def swap(source_img_name, target_img_name):
    # place swap function
    pass


def get_all_files(data_dir):

    if os.path.isdir(data_dir):
        return get_file_paths(data_dir)
    else:
        return read_file(data_dir, '\n')

def check_source_target(source, target):
    source_p_dir = re.split('\\\\|/', source)[-2]
    target_p_dir = re.split('\\\\|/', target)[-2]
    return source_p_dir != target_p_dir

def get_source_images(target_image, all_files, nums=1):
    source_images = []

    for _ in range(nums):
        i = np.random.randint(0, len(all_files))
        source_image = all_files[i]
        valid = check_source_target(source_image, target_image)
        while not valid:
            i = np.random.randint(0, len(all_files))
            source_image = all_files[i]
            valid = check_source_target(source_image, target_image)
        source_images.append(source_image)

    return source_images

if __name__ == '__main__':
    args = get_args()
    gen_nums = args.gen_nums
    data_dir = args.data_dir
    save_dir = args.save_dir
    ori_dir = args.ori_dir
    suffix = args.suffix

    all_files = get_all_files(data_dir)
    for target_file in tqdm(all_files):
        source_images = get_source_images(target_file, all_files, gen_nums)
        for i, source_image in enumerate(source_images):
            try:
                gen_img, mask = swap(source_image, target_file)
                save_path = target_file.replace(ori_dir, save_dir)
                save_path = save_path[:save_path.rfind('.')] + f'_{i}.{suffix}'
                make_path_legal(save_path)
                cv2.imwrite(save_path, gen_img)
                print(source_image, target_file, save_path)
            except:
                print(f'failed: {target_file}, {source_image}, {save_path}')

    
