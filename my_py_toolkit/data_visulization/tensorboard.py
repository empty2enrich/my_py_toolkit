# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

def visual_tensorboard(log_dir, tag, data, epoch, step):
  """

  Args:
    log_dir:
    tag:
    data(dict): example: {"date": []}
    epoch:
    step:

  Returns:

  """
  from tensorboardX import SummaryWriter
  for name, value in data.items():
    if value is None or len(value) < 1:
      # config.logger.warning(f"name: {name} Gradient is null")
      continue
    elif len(value) > 0:
      writer = SummaryWriter(f"{log_dir}/{name}")
      writer.add_histogram(f"{epoch}_{tag}", value, step)
      writer.close()