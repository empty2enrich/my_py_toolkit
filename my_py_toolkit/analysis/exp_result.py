# analysis exp result.
from my_py_toolkit.file.file_toolkit import *
from shutil import copy
import sys

def copyfiles(data_filter, data_dir, save_dir):
    for s, l, p in data_filter:
        fn = get_file_name(p)
        # print(f'fn: {fn}, in files mapping: {fn in files_mapping}')
        save_path = p.replace(data_dir, save_dir)
        save_path = save_path[:save_path.rfind('.')] + f'_{s}' + save_path[save_path.rfind('.'):]
        # save_path = os.path.join(save_dir, get_file_name(ori_path))
        make_path_legal(save_path)
        copy(p, save_path)

def filter_data(data, thr=0.5, label=None):
    error = []
    for s, l, p in zip(data['score'], data['label'], data['filenames']):
        if label is not None and label != l:
            continue
        
        if s >= thr and label == 0:
            error.append([s, l, p])
        if s < thr and label == 1:
            error.append([s, l, p])
    return error

def save_error_data(error_data, data_dir, save_dir):
    # real_dir = os.path.join(save_dir, 'real')
    # fake_dir = os.path.join(save_dir, 'fake')
    copyfiles(error_data, data_dir, save_dir)
    # copy_file

def filter_data_with_key(data, key):
    res = []
    for s, l ,p in data:
        if key in p:
            res.append((s, l, p))
    return res


def select_error_2_cls(score_label_path, data_dir, save_dir, split_keys, thr):
    # 1、读取数据，并筛选出错误数据
    # 2、保存错误数据，保留目录结构
    #   2.1、可根据关键字，保存到不同的目录

    # score_label_path = '/home/algtest/archive/problem_20230313/0222_code_modify/RECCE-nx/runs/Recce/cvpr2022_df_core_gclloss_reduce_channel_bmp_base_chan_8_add_real_and_screen_224_only_ljj_center_loss_add4v2_add_shine_real_back_normal_linear_only_gz_hn_0.9/score_label/191000_step_score_label.json'
    # data_dir = '/home/algtest/archive/1220/datasets'
    # save_dir = '/home/algtest/archive/1220/datasets_error/191000'
    # split_keys = {'v1.1_real':'real/', 'v1.1_fake':'fake/', 'gk': '_gz/', 'hn': 'hnbank', '240': '240/'}
    # thr = 0.5

    # 1、读取数据，并筛选出错误数据
    data = readjson(score_label_path)
    error_fake = filter_data(data, thr, 1)
    error_real = filter_data(data, thr, 0)
    # all_error = error_fake + error_real

    if not split_keys:
        real_dir = os.path.join(save_dir, 'real')
        fake_dir = os.path.join(save_dir, 'fake')
        save_error_data(error_real, data_dir, real_dir)
        save_error_data(error_fake, data_dir, fake_dir)
        print(f'errori imamge, real: {len(error_real)}, fake: {len(error_fake)}')
    else:
        for name, key in split_keys.items():
            cur_error_real = filter_data_with_key(error_real, key)
            cur_error_fake = filter_data_with_key(error_fake, key)
            cur_dir_real = os.path.join(save_dir, name, 'real')
            cur_dir_fake = os.path.join(save_dir, name, 'fake')

            save_error_data(cur_error_real, data_dir, cur_dir_real)
            save_error_data(cur_error_fake, data_dir, cur_dir_fake)

            print(f'errori imamge, {name} real: {len(cur_error_real)}, fake: {len(cur_error_fake)}')




