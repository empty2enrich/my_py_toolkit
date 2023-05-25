
import cv2
import numpy as np
from shutil import copy, move
from tqdm import tqdm
from my_py_toolkit.file.file_toolkit import *
from multiprocessing import Pool, cpu_count

def get_group_file(data_dir):
    res_group = []
    files = get_file_paths(data_dir, ['jpg'])
    files = sorted(files)
    
    cur = []
    for f in files:
        fn = get_file_name(f)
        if '_' not in fn:
            if cur:
                res_group.append(cur)
            cur = [f]
        else:
            cur.append(f)

    if cur:
        res_group.append(cur)

    return res_group

def read_image(paths, hw=448):
    nums = len(paths)
    print(f'nums images: {nums}')
    all_images = np.zeros([hw * 2, hw * nums // 2, 3], dtype=np.uint8)
    images = []
    for i, f in enumerate(paths):
        img = cv2.imread(f)
        img = cv2.resize(img, (hw, hw))
        h, w = i // (nums // 2) * hw , i %  (nums // 2) * hw
        # print(nums, h,w, all_images[h:h + hw, w:w + hw].shape)
        all_images[h:h + hw, w:w + hw,  :] = img
        # cv2.imshow('test', all_images)
        # cv2.waitKey(0)
        # print(all_images)
        # images.append(img)
    # images = [images[:nums//2], images[nums//2:]]
    # images = np.concatenate(images, axis=0)
    # images = images.reshape(hw * 2, hw * len(paths) // 2, 3)
    return all_images

def update_ids_images(ids, nums, stride):
    if stride > 0 and -1 < ids + stride * 2 < nums or (stride < 0 and -1 < ids + stride < nums):
        return ids + stride
    elif ids + stride < 0:
        return 1
    else:
        return nums - stride + 1

def copy_file(file, save_dir):
    new_path = os.path.join(save_dir, get_file_name(file))
    make_path_legal(new_path)
    copy(file, new_path)

def main():
    # 参数
    data_dir = r''
    paird_path = r'./res/paired.txt'
    unpaired_path = r'./res/unpaired.txt'
    paired_dir = r''
    unpaired_dir = r''
    log_path = './log'
    start_ids = 0
    nums_image = 8
    log = open(log_path, 'a+')

    
    # 读取所有文件，按 life id 分组
    res_group = get_group_file(data_dir)
    
    # 结果存储路径
    # pair_f = open(paird_path, 'a+')
    # unpair_f = open(unpaired_path, 'a+')
    
    
    # cv2 显示图片，并挑图
    # 控制: enter（13）:未配对； 左右, ad（97， 100）；上下, ws（119， 115）；
    # 1-9（49~57）: 选择配对
    # esc (27): 退出程序。
    
    # 窗口
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('test', 0)
    cv2.moveWindow('test', 0, 0)
    
    # 挑图
    bar = tqdm(range(len(res_group)))
    group_ids = start_ids
    while group_ids < len(res_group):
        group = res_group[group_ids]
        print(group[0], len(group))
        ids_images = 1
        while True:
            # read images
            paths = [group[0]] + group[ids_images: ids_images + nums_image -1]
            images = read_image(paths)
            # 显示
            cv2.imshow('test', images)
            # 控制
            k = cv2.waitKey()
            # 左右
            if k in [97, 100]:
                stride = nums_image if k == 100 else - nums_image
                ids_images = update_ids_images(ids_images, len(group), stride)
                print(f'左右 ids_images:{ids_images}')
            # 上下
            elif k in [119, 115]:
                if k == 119:
                    group_ids -= 1
                else:
                    group_ids += 1
                group_ids = max(0, group_ids)
                print(f'上下 group_ids： {group_ids}')
                break
            # 配对
            elif k in [v + 48 for v in [1, 2, 3, 4, 5, 6, 7, 8, 9]]:
                print(f'配对: {k}')
                # copy life
                copy_file(paths[0], paired_dir)
                # copy id
                copy_file(paths[k - 48], paired_dir)
                
                # pair_f = open(paird_path, 'a+')
                # life = get_file_name(paths[0])
                # id = get_file_name(paths[k - 49])
                # pair_f.write(f'{life} {id}\n')
                group_ids += 1 
                break
            # 未配对
            elif k == 13:
                print(f'未配对')
                # copy life
                copy_file(paths[0], unpaired_dir)
                # unpair_f = open(unpaired_path, 'a+')
                # life = get_file_name(paths[0])
                # unpair_f.write(f'{life}\n') 
                group_ids += 1  
                break
            elif k == 27:
                raise KeyboardInterrupt('Close program')
        log.write(f'group ids: {group_ids}, life: {group[0]}')
        bar.update(1)
            
# handle data

def copy_mul_thr(files, save_dir, ori_dir):
    result = []
    with Pool(cpu_count()) as p:
        for file in files:
            new_path = file.replace(ori_dir, save_dir)
            make_path_legal(new_path)
            p.apply_async(copy, (file, new_path))
        p.close()
        p.join()

        for r in result:
            print(r.get())

def split_dir_with_delete_info(ori_dir, handled_dir, save_dir):
    ori_files = get_file_paths(ori_dir)
    ori_files = [f.replace(ori_dir, '') for f in ori_files]
    handled_files = get_file_paths(handled_dir)
    handled_files = [f.replace(handled_dir, '') for f in handled_files]

    deleted_files = set(ori_files) - set(handled_files)
    deleted_files = [ori_dir + file for file in deleted_files]
    print(f'ori files: {len(ori_files)}, handled files: {len(handled_files)}, deleted files: {len(deleted_files)}')

    copy_mul_thr(deleted_files, save_dir, ori_dir)       
        
        
    

if __name__ == '__main__':
    main()