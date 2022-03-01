# -*- coding: utf-8 -*-
# Copyright
# Author:
#
# Tensor 的一些操作
#
# cython: language_level=3
#

import cv2 as cv
import math
import torch
from ..basic_data_type.basic_data_type_toolkit import *
from my_py_toolkit.file.file_toolkit import make_path_legal

def mask(tensor, tensor_mask, mask_dim, mask_value=0):
  """
  Mask a tensor.
  Args:
    tensor(torch.Tensor): 输入
    tensor_mask(torch.Tensor): mask 位置信息. 注：数据类型必须是 Int, 否则不能正确 mask。
    mask_dim(int): 负数，指定需要 mask 的维度，example：mask_dim = -1, 表示在最后一维上做 mask 操作.
      example: tensor is shape(3,3,3), -1 表示对最后一维的 len=3 的数组做 mask.
  Returns:
  """
  if not mask_dim < 0:
    raise Exception(f"Mask dim only supports negative numbers! Mask dim: {mask_dim} ")
  # to(bool) 原因: 使用 cuda 时, masked_fill 不支持 mask_tensor 为非 bool, 使用 cpu 时无影响 
  tensor_mask = ~ tensor_mask.to(bool)
  if mask_dim < 0:
    mask_dim = tensor.dim() + mask_dim
  for _ in range(mask_dim - tensor_mask.dim() + 1):
    tensor_mask = tensor_mask.unsqueeze(1)
  for _ in range(tensor.dim() - tensor_mask.dim()):
    tensor_mask = tensor_mask.unsqueeze(-1)
  return tensor.masked_fill(tensor_mask, mask_value)

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


def get_parameter_values(model):
  """

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

def gelu(tensor):
  cdf = 0.5 *(1.0 + torch.erf(tensor/math.sqrt(2.0)))
  return tensor * cdf

def save_tensor_as_picture(tensor, path):
  """
  将 torch 的 tensor 存为图片。
  Args:
    tensor:
    path(str):

  Returns:

  """
  make_path_legal(path)
  cv.imwrite(path, tensor.numpy())

def reshape_tensor(tensor, shape):
  return tensor.contiguous().view(*shape)