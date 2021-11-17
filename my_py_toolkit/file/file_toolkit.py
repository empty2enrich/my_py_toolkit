# -*- coding: utf-8 -*-
# Copyright  .
# Author:
#
# cython: language_level=3
#

import json
import os
import re

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

def make_path_legal(file_path):
  """"""
  if not os.path.exists(os.path.dirname(file_path)):
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