# -*- coding: utf-8 -*-
# Copyright
# Author:
#
# cython: language_level=3
#

from ..basic_data_type.basic_data_type_toolkit import *

def mask(tensor, tensor_mask, mask_dim):
  """
  Mask a tensor.
  Args:
    tensor(torch.Tensor): 输入
    tensor_mask(torch.Tensor): mask 位置信息.
    mask_dim(int): 负数，指定需要 mask 的维度，example：mask_dim = -1, 表示在最后一维上做 mask 操作.
  Returns:
  """
  if not mask_dim < 0:
    raise Exception(f"Mask dim only supports negative numbers! Mask dim: {mask_dim} ")

  for i in range(-mask_dim - 1):
    tensor_mask = tensor_mask.unsqueeze(-1)
  return tensor * tensor_mask

def get_gradient(model):
  """

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