# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

import os
import re

def get_file_paths(dir_name:str, file_type=None) -> list:
  """
  Gets all file path.
  Args:
    dir_name(str): The dir name.
    file_type:

  Returns:
    file_paths(list):
  """
  file_paths = []
  for dir_name, _, files in os.walk(dir_name):
    for file in files:
      file_paths.append(os.path.join(dir_name, file))
  return file_paths

def get_file_name(file_path):
  """"""
  return re.split("\\\\|/", file_path)[-1]
