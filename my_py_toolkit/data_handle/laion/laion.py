import os
import requests
import sys
import pyarrow as pa
import pyarrow.parquet as pq
from multiprocessing import cpu_count, Pool
# from my_py_toolkit.file.file_toolkit import *

# ============================ 根据 url 下载图像
def make_path_legal(file_path):
  """"""
  if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))

def download_from_url(url, save_path):
    content = requests.get(url).content
    with open(save_path, 'wb') as w:
        w.write(content)

# def hand_parquet(path, save_dir):
#     df = pq.read_table(path).to_pandas()

def get_suff(url):
    suff = url[url.rfind(".") + 1:]
    if suff not in ['jpg', 'png', 'bmp', 'gif', 'webp', 'cr2', 'tif', 'jxr', 'psd', 'ico']:
        suff = 'jpg'

    return suff

def main():
    data_dir, save_dir = sys.argv[1:3]
    result = []
    file_cts = 0 # 下载图像数
    split_nums = 50000
    keys = ['SAMPLE_ID', 'URL', 'TEXT']
    with Pool(cpu_count()) as p:
        for file in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file)
            df = pq.read_table(file_path).to_pandas()
            row_nums, col_nums = df.shape
            for i in range(row_nums):
                try:
                    print(i)
                    sample_id, url, caption = [df.loc[i][k] for k in keys]
                    suff = get_suff(url)
                    save_path = os.path.join(save_dir, 
                                            f'{file_cts // split_nums}', 
                                            f'{sample_id}.{suff}')
                    make_path_legal(save_path)
                    result.append(p.apply_async(download_from_url, (url, save_path)))
                    file_cts += 1
                except:
                    print(f'failed: {i}')

# 处理映射关系


