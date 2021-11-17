# -*- encoding: utf-8 -*-
#
# Author: LL
#
# Transformer 模型相关内容。
#
# cython: language_level=3

import math
import torch

def gen_pos_emb(seq_len, dim, pe_type='normal'):
    """
    生成 pisotion embedding 位置编码。

    Args:
        seq_len (int): 序列长度
        dim (int): 位置编码的维度
        pe_type (str, optional): 位置编码类型：normal or relative. Defaults to 'normal'.
    """
    assert dim%2 == 0
    div_term = torch.exp(torch.arange(0, dim, 2) * (- math.log(10000)/dim))
    pe = None
    if pe_type == 'relative':
        pe = torch.zeros((seq_len * 2 - 1, dim))
        pos = torch.arange(-seq_len + 1, seq_len).unsqueeze(1)
    else:
        pe = torch.zeros((seq_len, dim))
        pos = torch.arange(0, seq_len).unsqueeze(1)
    pe[:, 0::2] = torch.sin(pos * div_term)
    pe[:, 1::2] = torch.cos(pos * div_term)
    return pe
