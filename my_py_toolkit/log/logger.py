# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

import os
import logging

def get_logger(log_file_path=None, info_level=logging.DEBUG):
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)
  logger.setLevel(level=info_level)

  console = logging.StreamHandler()
  console.setLevel(info_level)
  console.setFormatter(formatter)
  logger.addHandler(console)

  if log_file_path:
    if not os.path.exists(os.path.dirname(log_file_path)):
      os.makedirs(os.path.dirname(log_file_path))
    handler = logging.FileHandler(log_file_path, encoding="utf-8")
    handler.setLevel(info_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
  return logger