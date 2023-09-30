from shutil import move, copy
from my_py_toolkit.file.file_toolkit import *
import os
from tqdm import tqdm


def get_miss_files_with_filename(data_ori_dir, data_handle_dir, data_miss_dir, suffix=[]):
    """
    清洗数据时，找出清洗过程删掉的数据。
        1、根据文件名判断文件是否删除。
    """
    ori_files = get_file_paths(data_ori_dir, suffix)
    handle_files = get_file_paths(data_handle_dir, suffix)
    handle_files = [get_file_name(f) for f in handle_files]
    for file in tqdm(ori_files):
        if get_file_name(file) in handle_files:
            continue
        
        new_path = file.replace(data_ori_dir, data_miss_dir)
        make_path_legal(new_path)
        copy(file, new_path)