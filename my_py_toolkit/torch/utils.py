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
    try:
      config.logger.info(
        f"Continue train, epoch:{config.continue_epoch}, continue_checkpoint: {config.continue_checkpoint}")
      optimizer_path = os.path.join(config.model_save_dir,
                                    f"optimizer_epoch{config.continue_epoch}_step{config.continue_checkpoint}.pkl")
      if not config.is_only_save_params:
        optimizer = torch.load(optimizer_path, map_location=config.device)
      else:
        optimizer = torch.optim.Adam(lr=config.learning_rate,
                                     betas=(config.beta1, config.beta2),
                                     eps=1e-8, weight_decay=3e-7, params=params)
        optimizer.load_state_dict(torch.load(optimizer_path))
    except Exception as e:
      # 训练过程中如果时不时冻结一些网络继续训练， load_state_dict 会出问题，返回一个新的 optimizer
      params = get_model_trainabel_param(model)
      optimizer = torch.optim.Adam(lr=config.learning_rate,
                                   betas=(config.beta1, config.beta2),
                                   eps=1e-8, weight_decay=3e-7, params=params)
    return optimizer


def sequence_mask(X, valid_len, value=0):
  """
  屏蔽 pad 位置的值
  """
  maxlen = X.shape[1]
  mask = torch.arange((maxlen), dtype=torch.float32, device=X.device)[None,:] < valid_len[:, None]
  X[~mask] = value
  return X


def load_bert(bert_cfg, use_pretrained=False, freeze_params=False, device='cpu'):
  """
  加载预训练好的 BERT 参数。

  Args:
      bert_cfg (str): bert 模型的配置信息; 
        1、若初始化一个新的 BERT 模型， bert_cfg 为 bert config.json 路径；
        2、若加载训练好的 BERT, bert_cfg 为 bert 模型所在文件夹路径
      use_pretrained(bool): 是否加载预训练模型。
      freeze_params(bool): 是否固定 bert 参数。
      device(str): 设备，cpu or cuda.
  """
  from transformers.modeling_bert import BertConfig, BertModel
  model = None
  if use_pretrained:
    model = BertModel.from_pretrained(bert_cfg).to(device)
  else:
    model = BertModel(BertConfig(bert_cfg))
  
  if freeze_params:
    for param in model.parameters():
      param.requires_grad = False
  
  return model


# k folder 交叉验证
def get_k_folder(*data, k=2):
    """
    k 折交叉验证, 把数据切成 K 份，每次选择其中一份为测试数据，剩下为训练数据

    Args:
        data(list, np.array, tensor):
        k (int, optional): k 折. Defaults to 2.
    """
    if len(data) < 1:
        raise ValueError('data must not be empty!')
    def merge(a, b):
        if isinstance(a, list):
            return a + b
        elif isinstance(a, np.ndarray):
            return np.concatenate((a,b))
        elif isinstance(a, torch.Tensor):
            return torch.cat((a,b))

    l = len(data[0])
    avg = l // k
    for i in range(k):
        train_d = [merge(d[:i * avg], d[(i+1)*avg:]) for d in data]
        test_d = [d[i * avg: (i+1)*avg] for d in data]
        yield train_d, test_d