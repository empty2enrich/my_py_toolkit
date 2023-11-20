import requests
from bs4 import BeautifulSoup
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

def writejson(data, file_path):
  """"""
  make_path_legal(file_path)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(data, ensure_ascii=False, indent=2))


# 获取症状信息
def handle_value(value):
    value = value.replace('?', '')
    return value

def get_zhengzhuang(html):
    soup = BeautifulSoup(open(html, 'r', encoding='utf-8'), 'html.parser')
    result = {'common_symptoms': [], 'all_symptoms': []}
    # 常见症状
    com = soup.find_all('div', "jblist-bd bor")
    if com:
        for item in com[0].find_all('a'):
            if item['title']:
                result['common_symptoms'].append(handle_value(item['title']))
    # 所有症状
    all_sym = soup.find_all('div', "fl jblist-con-ill")
    if all_sym:
        for item in all_sym[0].find_all('a'):
            if item['title']:
                result['all_symptoms'].append(handle_value(item['title']))
    return result

def handle_all_html(data_dir, keshi_info):
    result = {}

    for p_t, pt_info in keshi_info.items():
        if p_t not in result:
            result[p_t] = {}

        for sub_title, href in pt_info.items():
            html_file = os.path.join(data_dir, p_t, sub_title, href.split('/')[-1])
            result[p_t][sub_title] = get_zhengzhuang(html_file)
    return result

if __name__ == '__main__':
    info = readjson('./datas/keshi_mulu_info.json')
    all_zhengzhuang = handle_all_html(data_dir='./datas/htmls/', keshi_info=info)
    writejson(all_zhengzhuang, './datas/all_symptoms.json')

