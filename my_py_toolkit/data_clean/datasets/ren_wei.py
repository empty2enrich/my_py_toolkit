# from my_py_toolkit.file.file_toolkit import  *
import sys


import json
import os
import re
import sys
from tqdm import tqdm



def read_file(path, spl_char=None, ops=None, encoding='utf-8'):
    """
    读取文件内容, 并使用分隔符分割文本，对分割文本进行处理。

    Args:
        path (str): 文件路径
        spl_char (str, optional): 文件内容分隔符，eg: \n, 表示把文件内容按 \n 分成数组. Defaults to None.
        ops(function): 对值的处理函数
    """
    # TODO 后期把编码改 utf-8 试试
    with open(path, 'r', encoding=encoding) as f:
        data = f.read()
        if spl_char is not None:
            data = data.split(spl_char)
        if ops:
            data = ops(data)
        return data


def get_file_paths(dir_name:str, file_suffix=[]) -> list:
  """
  Gets all file path.
  Args:
    dir_name(str): The dir name.
    file_suffix(list): The suffix of file.

  Returns:
    file_paths(list):
  """
  file_paths = []
  file_suffix = [v.replace(".", "") for v in file_suffix]
  for dir_name, _, files in os.walk(dir_name):
    for file in files:
      if not file_suffix or get_file_suffix(file) in file_suffix:
        file_paths.append(os.path.join(dir_name, file))
  return file_paths

def get_file_name(file_path):
  """
  Get file name.
  Anther implement: os.path.split(file_path)[-1]
  Args:
    file_path:

  Returns:

  """
  return re.split("\\\\|/", file_path)[-1]

def get_file_suffix(file_path):
  """"""
  return file_path[file_path.rfind(".") + 1:]

def readjson(file_path):
  """"""
  make_path_legal(file_path)
  with open(file_path, "r", encoding="utf-8") as f:
    return json.load(f)

def make_path_legal(file_path):
  """"""
  if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))

def writejson(data, file_path):
  """"""
  make_path_legal(file_path)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(data, ensure_ascii=False, indent=2))

def handle_rich_text(value):
    result = ''
    start_pre = 0
    for search in re.finditer('<.?\w+[ ]*[^>]*>', value):
        if search.group() not in ['<sub>', '</sub>', '<sup>', '</sup>']:
            start, end = search.span()
            result += value[start_pre:start]
            start_pre = end
    result += value[start_pre:]
    return result

def handle_content(value):
    # sub, sup
    value = handle_rich_text(value)
    value = value.replace('\t', '\n')
    return value

def handle_content_dict(value):
    cur = {}
    name_mapping = {
        'name': '名称',
        'source': '来源',
        'value': '内容'
    }
    for name_en, name_zh in name_mapping.items():
        cur[name_zh] = value.get(name_en, '')
        if name_en == 'value':
            cur[name_zh] = handle_content(cur[name_zh])
    return cur

def handle_content_string(value):
    cur = ''
    name_mapping = {
        'name': '名称',
        'source': '来源',
        'value': '内容'
    }
    for name_en in name_mapping:
        if name_en in value:
            if name_en == 'value':
                cur += handle_content(value.get(name_en, '')) + '\n'
            else:
                cur += value.get(name_en, '') + '\n'
    return cur

def get_meta_data(data):
    res = {}
    name_mapping = {
        'createTime': '创建时间',
        'tagIds': '标签 ID',
        'tagNames': '标签名称',
        'updateTime': '更新时间'
    }
    for name_en, name_zh in name_mapping.items():
        res[name_zh] = data.get(name_en, '')
    return res


def handle_data_dict(path, file_info):
    # print(path)
    fn = get_file_name(path)
    result = {'内容': [], '文件': fn, '文件信息': file_info}
    data = readjson(path)
    # 检测改网页是否爬取成功
    if data['code'] != 200:
        return {'文件': fn, 'code': data['code'], '内容':'网页爬取识别', '文件信息': file_info}

    # 提取内容
    meta_data = get_meta_data(data['data'])
    result.update(meta_data)
    
    for item in data['data']['attributes']:
        item = json.loads(item)
        # print(item)
        if 'children' not in item:# and 'name' in item:
            result[item['name']] = item['value']
        elif 'children' in item:
            result['内容'].append(handle_content_dict(item))
    
    return result

def handle_data_string(path, file_info):
    fn = get_file_name(path)
    result = {'内容': '', '文件': fn, '文件信息': file_info}
    data = readjson(path)
    # 检测改网页是否爬取成功
    if data['code'] != 200:
        return {'文件': fn, 'code': data['code'], '内容':'网页爬取识别', '文件信息': file_info}

    # 提取内容
    meta_data = get_meta_data(data['data'])
    result.update(meta_data)
    
    for item in data['data']['attributes']:
        item = json.loads(item)
        if 'children' not in item:
            result[item['name']] = item['value']
        elif 'children' in item:
            result['内容'] += handle_content_string(item)
    
    return result

def write2file(writer, value):
    writer.write(json.dumps(value, ensure_ascii=False) + '\n')

def get_info(data_dir):
    result = {}
    path = os.path.join(data_dir, 'text_id_path.txt')
    for line in read_file(path, '\n'):
        if not line:
            continue
        # print(line)
        key, value = line.split('	')
        value = value[:value.rfind('.')]
        cur_res = value.split('/')[2:] #[v.group() for v in (re.finditer('(?<=#)[\u4e00-\u9fa5]+', value))]
        result[get_file_name(key)] = cur_res
    return result

def main():
    data_dir, dict_path, string_path, error_path = sys.argv[1:5]

    writer_dict_res = open(dict_path, 'w', encoding='utf-8')
    writer_dict_string = open(string_path, 'w', encoding='utf-8')
    writer_error = open(error_path, 'w', encoding='utf-8')

    file_info = get_info(data_dir)
    for file in tqdm(get_file_paths(data_dir)):
        fn = get_file_name(file)
        if fn == 'text_id_path.txt':
            continue

        dict_res = handle_data_dict(file, file_info.get(fn, []))
        string_res = handle_data_string(file, file_info.get(fn, []))
        if 'code' in dict_res:
            write2file(writer_error, dict_res)
        else:
            write2file(writer_dict_res, dict_res)
            write2file(writer_dict_string, string_res)

if __name__ == '__main__':
    main()

