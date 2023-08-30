from my_py_toolkit.file.file_toolkit import *
from shutil import copy
from multiprocessing import Pool, cpu_count
import sys

def copy_files_multi(files, data_dir, save_dir):
    # random.shuffle(files)
    with Pool(cpu_count()) as pool:
        result = []
        for file, dis in files:
            new_path = file.replace(data_dir, save_dir)
            new_path = new_path[:new_path.rfind('.')] + f'_{dis:.4f}' + new_path[new_path.rfind('.'):]
            make_path_legal(new_path)
            pool.apply_async(copy, (file, new_path))
        pool.close()
        pool.join()
        for _ in result:
            print(_.get())

def main():
    cluster_res_path, ori_dir, save_dir = sys.argv[1:4]
    cluster_res = readjson(cluster_res_path)
    for i, paths in cluster_res.items():
        cur_save_dir = os.path.join(save_dir, str(i))
        copy_files_multi(paths, ori_dir, cur_save_dir)





if __name__ == '__main__':
    main()