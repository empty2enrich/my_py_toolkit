# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

from my_py_toolkit.torch.utils import get_gradient, get_parameter_values, process_optimizer_info

def visual_tensorboard(log_dir, tag, data, epoch, step):
  """
  使用 tensorboard 可视化数据
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

def is_last_layer(value):
  if not isinstance(value, dict):
    return True
  for k,v in value.items():
    if isinstance(v, dict):
      return False
  return True

def transfer_multi_layer_dict(dict_value):
  """
  将多层 dict 转换为 1 层 dict.
  Args:
    dict_value:

  Returns:

  """
  result = {}
  for key, value in dict_value.items():
    if not isinstance(value, dict):
      result[key] = value
      continue


    if not is_last_layer(value):
      value = transfer_multi_layer_dict(value)

    for sub_key, sub_value in value.items():
      result[f"{key}.{sub_key}"] = sub_value

  return result


def visual_data(model, epoch, step, loss=None, optimizer=None, exact_match_total=None,
                f1_total=None, exact_match=None, f1=None, label="train", visual_gradient=False,
                visual_gradient_dir="", visual_parameter=False,
                visual_parameter_dir=None, visual_loss=False,
                visual_loss_dir="", visual_optimizer=False,
                visual_optimizer_dir="", visual_valid_result=False,
                visual_valid_result_dir=None):
  """
  可视化训练信息。
  Args:
    model:
    loss:
    epoch:
    step:

  Returns:

  """
  if visual_gradient:
    gradient = get_gradient(model)
    gradient = transfer_multi_layer_dict(gradient)
    visual_tensorboard(visual_gradient_dir, f"{label}_gradient",
                       gradient, epoch, step)
  if visual_parameter:
    parameter_values = get_parameter_values(model)
    parameter_values = transfer_multi_layer_dict(parameter_values)
    visual_tensorboard(visual_parameter_dir, f"{label}_parameter_values",
                       parameter_values, epoch, step)
  if visual_loss:
    visual_tensorboard(visual_loss_dir, f"{label}_loss", {"loss": [loss.item()]},
                       epoch, step)
  if visual_optimizer:
    visual_tensorboard(visual_optimizer_dir, f"{label}_optimizer",
                       process_optimizer_info(optimizer), epoch, step)
  if visual_valid_result:
    visual_tensorboard(visual_valid_result_dir, f"{label}_valid", {
      "exact_match_total": [exact_match_total],
      "exact_match": [exact_match],
      "f1_total": [f1_total],
      "f1": [f1]
    }, epoch, step)