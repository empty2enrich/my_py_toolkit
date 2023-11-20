# from my_py_toolkit.file.file_toolkit import *
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import traceback
import json

def make_path_legal(file_path):
  """"""
  if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))

def readjson(file_path):
  """"""
  make_path_legal(file_path)
  with open(file_path, "r", encoding="utf-8") as f:
    return json.load(f)

prefix = 'https://zzk.xywy.com/'
data = readjson('./datas/keshi_mulu_info.json')
save_dir = './datas/htmls/'

for p_t, pt_info in tqdm(data.items()):
    for sub_title, sub_url in pt_info.items():
        url = f'{prefix}{sub_url}'
        try:
            res = requests.get(url)
            
            save_path = os.path.join(save_dir, p_t, sub_title, sub_url.split('/')[-1])
            make_path_legal(save_path)
            with open(save_path, 'w') as w:
                w.write(res.content.decode('gbk'))

        except:
            print(f'failed {sub_title}, {traceback.format_exc()}')
