# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3

import torch


def log_sum_exp(vec, m_size):
    """
    calculate log of exp sum
    args:
        vec (batch_size, vanishing_dim, hidden_dim) : input tensor
        m_size : hidden_dim
    return:
        batch_size, hidden_dim
    """
    # 防止溢出：log sum exp (x1,x2..,xn) 时先将所有 x 减去最大值 max(x1,..xn)，计算 log sum exp 完, 最后再把最大值加回来。
    _, idx = torch.max(vec, 1)  # B * 1 * M
    max_score = torch.gather(vec, 1, idx.view(-1, 1, m_size)).view(-1, 1, m_size)  # B * M
    return max_score.view(-1, m_size) + torch.log(torch.sum(torch.exp(vec - max_score.expand_as(vec)), 1)).view(-1, m_size)  # B * M