#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:LL
# 2019

def add_value4dict(value_dict, *args):
  args_len = len(args)
  if args_len == 2:
    value_dict[args[0]] = args[1]
    return value_dict
  elif args_len > 2:
    value_dict[args[0]] = add_value4dict({}, *args[1:])
    return value_dict
  else:
    raise Exception(f"Args length must longer than 2, now ars is :{args}")

def append_value4dict(value_dict, *args):
  args_len = len(args)
  if args_len == 2:
    if args[0] in value_dict:
      value_dict[args[0]].append(args[1])
    else:
      value_dict[args[0]] = [args[1]]
  else:
    if args[0] in value_dict:
      value_dict[args[0]] = append_value4dict(value_dict[args[0]], *args[1:])
    else:
      value_dict[args[0]] = append_value4dict({}, *args[1:])
  return value_dict

if __name__ == "__main__":
  a = append_value4dict({}, *[ str(i) for i in range(1,8)])
  print(append_value4dict(a, *[ str(i) for i in range(1,8)]))
