# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3

import numpy as np
import torch



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
        if len(data) > 1:
            train_d = [merge(d[:i * avg], d[(i+1)*avg:]) for d in data]
            test_d = [d[i * avg: (i+1)*avg] for d in data]
            yield train_d, test_d
        else:
            data = data[0]
            train_d = merge(data[:i * avg], data[(i+1) * avg:])
            test_d = data[i * avg: (i+1) * avg]
            yield train_d, test_d

