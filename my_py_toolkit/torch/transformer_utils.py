# -*- encoding: utf-8 -*-
#
# Author: LL
#
# Transformer 模型相关内容。
#
# cython: language_level=3

import math
from re import S
from turtle import forward
import torch

from torch.functional import F
from .tensor_toolkit import mask

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

####################################################################################################
###################################### transformer encoder、decoder 实现 ############################################
####################################################################################################

def generate_mask_matrix(mask, mask_type='padding'):
    """
    生成 mask 矩阵。

    Args:
        mask (Tensor): [description]
        mask_type (str, optional): mask 类别： padding  、attention , . Defaults to 'padding'.
            padding 指 mask 掉 [PAD] 的部分， attention 指 transformer 解码器解码时，当前  token 只能看到前面的，需要把后面的 token attention score mask。

    Returns:
        [type]: [description]
    """
    if mask_type == 'padding':
        mask = ((1.0 - mask) * -10000.0).unsqueeze(-2)
        return mask
    elif mask_type == 'attention':
        batch_size, len_seq = mask.size()
        mask = mask.unsqueeze(-2).expand(batch_size, len_seq, len_seq)
        mask = torch.triu(mask.permute(0, 2, 1), diagonal=0).permute(0, 2, 1)
        mask += (1.0 - mask) * -10000.0
        return mask
    else:
        raise Exception(f"Mask type only supports padding or attention! mask_type: {mask_type}")

class SelfAttention(torch.nn.Module):
    def __init__(self, dim_model, num_head, dropout=0.1):
        super().__init__()
        self.num_head = num_head
        self.drop_out = dropout
        self.dim_head = dim_model // num_head
        self.q = torch.nn.Linear(dim_model, self.num_head * self.dim_head)
        self.k = torch.nn.Linear(dim_model, self.num_head * self.dim_head)
        self.v = torch.nn.Linear(dim_model, self.num_head * self.dim_head)
        self.out = torch.nn.Linear(self.num_head * self.dim_head, dim_model)

    def forward(self, hidden_status, attention_mask=None, head_mask=None):
        batch_size, len_seq, _ = hidden_status.size()
        query = self.q(hidden_status)
        key = self.k(hidden_status)
        val = self.v(hidden_status)
        # batch_size, num_head, len_seq, dim_head
        query = query.view(batch_size, len_seq, self.num_head, self.dim_head).permute(0, 2, 1, 3)
        key = key.view(batch_size, len_seq, self.num_head, self.dim_head).permute(0, 2, 1, 3)
        value = val.view(batch_size, len_seq, self.num_head, self.dim_head).permute(0, 2, 1, 3)
        # batch_size, num_head, len_seq, len_seq
        attention = query @ key.transpose(-1, -2) / math.sqrt(self.dim_head)
        if attention_mask is not None:
            attention += generate_mask_matrix(attention_mask, mask_type='padding')
        attention = F.softmax(attention, dim=-1)
        attention = F.dropout(attention, p=self.drop_out, training=self.training)
        output = attention @ value
        output = output.permute(0, 2, 1, 3).contiguous()
        output = output.view(batch_size, len_seq, self.num_head * self.dim_head)
        output = self.out(output)
        return output, attention
        
class Encoder(torch.nn.Module):
    def __init__(self, dim_model, num_head, dropout, dim_intermidiate):
        super().__init__()
        self.dropout = dropout
        self.atten = SelfAttention(dim_model, num_head, dropout)
        self.intermidiate = torch.nn.Linear(dim_model, dim_intermidiate)
        self.out = torch.nn.Linear(dim_intermidiate, dim_model)
        self.norm_att = torch.nn.LayerNorm(dim_model)
        self.norm_lin = torch.nn.LayerNorm(dim_model)
        self.relu = torch.nn.ReLU()
    
    def forward(self, hidden_status, attention_mask=None, head_mask=None):
        output, _ = self.atten(hidden_status, attention_mask, head_mask)
        output = F.dropout(output, self.dropout)
        output = self.norm_att(hidden_status + output)
        hidden_status = output
        # output = self.relu(output)
        output = self.intermidiate(output)
        output = self.relu(F.dropout(output, self.dropout))
        output = F.dropout(self.out(output))
        output = self.norm_lin(hidden_status + F.dropout(output))
        return output