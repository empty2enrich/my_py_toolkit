# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#
import copy
import numpy as np
import os
import torch
from my_py_toolkit.file.file_toolkit import make_path_legal

def add_value4dict(value_dict, *args):
  args_len = len(args)
  if args_len == 2:
    value_dict[args[0]] = args[1]
    return value_dict
  elif args_len > 2:
    value_dict[args[0]] = add_value4dict(value_dict.get(args[0], {}), *args[1:])
    return value_dict
  else:
    raise Exception(f"Args length must longer than 2, now ars is :{args}")


def get_gradient(model):
  """
  获取模型的梯度。
  Args:
    model:

  Returns:

  """
  gradients = {}
  for name, parameter in model.named_parameters():
    keys = name.split(".")
    grad = parameter.grad
    keys.append(grad)
    add_value4dict(gradients, *keys)
  return gradients


def get_parameter_values(model):
  """
  获取模型的参数。
  Args:
    model:

  Returns:

  """
  parameter_values = {}
  for name, parameter in model.named_parameters():
    keys = name.split(".")
    data = parameter.data
    keys.append(data)
    add_value4dict(parameter_values, *keys)
  return parameter_values

def process_optimizer_info(optimizer):
  """获取优化器的信息"""
  val = copy.deepcopy(optimizer.defaults)
  result = {}
  for k,v in val.items():
    if not isinstance(v, list):
      v = [v]
    result[k] = np.asarray(v)
  return result


def save_model(model, model_save_dir, optmizer=None, is_only_save_params=True,
               epoch=0, steps=0):
  """

  Args:
    model:
    optmizer:
    model_save_dir:
    is_only_save_params:
    epoch:
    steps:

  Returns:

  """
  model_path = os.path.join(model_save_dir, f"model_epoch{epoch}_step{str(steps)}.pkl")
  optimizer_path = os.path.join(model_save_dir, f"optimizer_epoch{epoch}_step{str(steps)}.pkl")
  make_path_legal(model_path)
  make_path_legal(optimizer_path)
  if not is_only_save_params:
    torch.save(model, model_path)
    if optmizer:
      torch.save(optmizer, optimizer_path)
  else:
    torch.save(model.state_dict(), model_path)
    if optmizer:
      torch.save(optmizer.state_dict(), optimizer_path)

def load_model(model_class, config):
  """
  load model
  Args:
    model_class:
    config:

  Returns:

  """
  model = model_class(config)
  if config.is_continue_train:
    model_path = os.path.join(config.model_save_dir,
                              f"model_epoch{config.continue_epoch}_step{config.continue_checkpoint}.pkl")
    if config.is_only_save_params:
      model.load_state_dict(torch.load(model_path))
    else:
      model = torch.load(model_path, map_location=config.device)
  model.to(config.device)
  return model


def get_model_trainabel_param(model):
  params = filter(lambda param: param.requires_grad, model.parameters())
  return params

def get_adam_optimizer(model, config):
  """
  Gets optimizer.
  Returns:

  """
  params = get_model_trainabel_param(model)
  if not config.is_continue_train:
    return torch.optim.Adam(lr=config.learning_rate, betas=(config.beta1, config.beta2),
                         eps=1e-8, weight_decay=3e-7, params=params)
  else:
    config.logger.info(f"Continue train, epoch:{config.continue_epoch}, continue_checkpoint: {config.continue_checkpoint}")
    optimizer_path = os.path.join(config.model_dir,
                              f"optimizer_epoch{config.continue_epoch}_step{config.continue_checkpoint}.pkl")
    if not config.is_only_save_params:
      optimizer = torch.load(optimizer_path, map_location=config.device)
    else:
      optimizer = torch.optim.Adam(lr=config.learning_rate, betas=(config.beta1, config.beta2),
                         eps=1e-8, weight_decay=3e-7, params=params)
      optimizer.load_state_dict(torch.load(optimizer_path))
    return optimizer