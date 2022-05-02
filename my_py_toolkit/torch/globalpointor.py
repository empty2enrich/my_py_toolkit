# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3

import torch
from .tensor_toolkit import mask
from .transformer_utils import gen_pos_emb


####################################################################################################
###################################### Global Pointor ############################################
####################################################################################################


def rope(inputs):
    """rotary position embedding"""
    device = inputs.device
    length, dim = inputs.shape[-2:]
    pos = gen_pos_emb(length, dim)
    inputs_2 = torch.zeros_like(inputs)
    inputs_2[..., ::2] = -inputs[..., 1::2]
    inputs_2[..., 1::2] = inputs[..., ::2]
    sin, cos = torch.zeros_like(pos), torch.zeros_like(pos)
    sin[:, ::2], sin[:, 1::2] = pos[:, ::2], pos[:, ::2]
    cos[:, ::2], cos[:, 1::2] = pos[:, 1::2], pos[:, 1::2]
    return inputs * cos.to(device) + inputs_2 * sin.to(device)

def multilabel_categorical_crossentropy(y_true, y_pre):
    y_pre = (1 - 2* y_true) * y_pre
    y_neg = mask(y_pre, y_true, -1, -10000)
    y_pos = mask(- y_pre, 1 - y_true, -1, -10000)
    zero = torch.zeros_like(y_true[..., :1])
    y_neg = torch.cat([y_neg, zero], -1)
    y_pos = torch.cat([y_pos, zero], -1)
    return torch.logsumexp(y_neg, -1) + torch.logsumexp(y_pos, -1)


def global_pointer_loss(y_true, y_pre):
    b, h = y_pre.shape[:2]
    y_pre = y_pre.reshape(b*h, -1)
    y_true = y_true.permute(0, 3, 1, 2).reshape(b*h, -1)
    return torch.mean(multilabel_categorical_crossentropy(y_true, y_pre))

def f1_globalpointer(y_true, y_pre, tp_pre=None, tpfp_pre=None, tpfn_pre=None):
    y_pre = y_pre.greater(0)
    if tp_pre is None:
        return 2 * (y_true * y_pre).sum() / (y_true.sum() + y_pre.sum())
    else:
        tp = (y_true * y_pre).sum() + tp_pre
        tpfp = y_pre.sum() + tpfp_pre
        tpfn = y_true.sum() + tpfn_pre
        return 2 * tp / (tpfp + tpfn), tp, tpfp, tpfn


# f1_globalpointer_sparse
def f1_globalpointer_sparse(y_true, y_pre, tp_pre=None, tpfp_pre=None, tpfn_pre=None):
    batch_size, labels_num, seq_len, _ = y_pre.shape
    y_true = y_true[..., 0] * seq_len + y_true[..., 1]
    y_pre = y_pre.reshape(batch_size, labels_num, -1)
    y_pre = (y_pre)>0

    tp = y_pre.gather(-1, y_true).sum()
    tpfp = y_pre.sum()
    tpfn = (y_true > 0).sum()
    
    if tp_pre is None:
        return 2*tp / (tpfp + tpfn)
    else:
        tp += tp_pre
        tpfp += tpfp_pre
        tpfn += tpfn_pre
        return 2*tp / (tpfp + tpfn), tp, tpfp, tpfn


def em_globalpoiter(y_true, y_pre, tp_pre=None, tpfp_pre=None):
    y_pre = y_pre.greater(0)
    if tp_pre is None:
        return (y_true * y_pre).sum()/ y_pre.sum() 
    else:
        tp = (y_true * y_pre).sum() + tp_pre
        tpfp = y_pre.sum() + tpfp_pre
        return tp/tpfp, tp, tpfp

# em_globalpointer_sparse
def em_globalpointer_sparse(y_true, y_pre, tp_pre=None, tpfp_pre=None):
    batch_size, labels_num, seq_len, _ = y_pre.shape
    y_true = y_true[..., 0] * seq_len + y_true[..., 1]
    y_pre = y_pre.reshape(batch_size, labels_num, -1) > 0
    if tp_pre is None:
        return y_pre.gather(-1, y_true).sum() / y_pre.sum()
    else:
        tp = y_pre.gather(-1, y_true).sum() + tp_pre
        tpfp = y_pre.sum() + tpfp_pre
        return tp / tpfp, tp, tpfp

def predict_globalpointer(y_pre, tags):
    res = [{}] * y_pre.shape[0]
    idx = (y_pre>0).nonzero()
    for b, tag_idx, start, end in idx.tolist():
        if tags[tag_idx] not in res[b]:
            res[b][tags[tag_idx]] = []
        res[b][tags[tag_idx]].append((start, end))
    return res
    

def predict_globalpointer_compare(y_pre, tags):
    res = [[] for _ in range(y_pre.shape[0])]
    idx = (y_pre>0).nonzero()
    for b, tag_idx, start, end in idx.tolist():
        res[b].append((tags[tag_idx], (start, end)))
        
    return res

def handle_true_sparse(y_true, tags):
    """"""
    res = []
    for t in y_true.tolist():
        cur_res = []
        for tag_id, scopes in enumerate(t):
            for s, e in scopes:
                if s == 0 and e == 0:
                    continue
                cur_res.append((tags[tag_id], (s, e)))
        res.append(cur_res)
    return res

def compare_res(y_pre, y_true, tags, txts, new2ori_idxs, sparse=False):
    y_pre = predict_globalpointer_compare(y_pre, tags)
    y_true = predict_globalpointer_compare(y_true, tags) if not sparse else handle_true_sparse(y_true, tags)
    res = []
    for y_pre_cur, y_true_cur, txt, new2ori_idx in zip(y_pre, y_true, txts, new2ori_idxs):
        y_pre_cur, y_true_cur = set(y_pre_cur), set(y_true_cur)
        cur_res = {}
        pre_res, true_res = [], []
        for tag, (start, end) in y_pre_cur - y_true_cur:
            # 减一原因：第一个 token 为 [CLS]
            if all([start > len(new2ori_idx), end > len(new2ori_idx)]):
                # print(f'start: {start}, end: {end}, tokens num:{len(new2ori_idx)}')
                continue
            end = min(end - 1, len(new2ori_idx) - 1)
            start_txt, end_txt = new2ori_idx[start - 1][0], new2ori_idx[end][1]
            ner_txt = txt[start_txt:end_txt]
            pre_res.append((tag, ner_txt, (start, end), (start_txt, end_txt)))
        for tag, (start, end) in y_true_cur - y_pre_cur:
            end = min(end - 1, len(new2ori_idx) - 1)
            start_txt, end_txt = new2ori_idx[start - 1][0], new2ori_idx[end - 1][1]
            ner_txt = txt[start_txt:end_txt]
            true_res.append((tag, ner_txt, (start, end), (start_txt, end_txt)))
        if pre_res:
            cur_res['pre'] = pre_res
        if true_res:
            cur_res['true'] = true_res
        if cur_res:
            cur_res['txt'] = txt
        if cur_res:
            res.append(cur_res)
    return res
    

def sparse_global_loss(y_true, y_pre):
    """
    y_true( batch_size, labes_num, 2)
    y_pre(batch_size, labels_num, seq_len, seq_len)

    """
    batch_size, labels_num, seq_len, _ = y_pre.shape
    y_true = y_true[..., 0] * seq_len + y_true[..., 1]
    y_pre = y_pre.reshape(batch_size, labels_num, -1)
    return torch.mean(spare_multilable_categorical_crossentropy(y_true, y_pre, True).sum(1))

def spare_multilable_categorical_crossentropy(y_true, y_pre, mask_zero=False, mask_value=-10000):
    """
    y_true(batch_size, labels_num, 1)
    y_pre(batch_size, labels_num, seq_len * seq_len)
    """
    # device = y_pre.device
    zeros = torch.zeros_like(y_true[..., :1])
    mask_tensor = torch.ones_like(y_pre[..., :1]) * mask_value
    if mask_zero:
        y_pre = torch.cat([- mask_tensor, y_pre[..., 1:]], dim=-1)

    y_pos = y_pre.gather(-1, y_true)
    y_pos_2 = torch.cat([ - y_pos, zeros], dim=-1)
    loss_pos = torch.logsumexp(y_pos_2, -1)

    y_pre = torch.cat([y_pre, zeros], -1)
    
    if mask_zero:
        y_pre = torch.cat([mask_tensor, y_pre[..., 1:]], dim=-1)

    loss_all = torch.logsumexp(y_pre, dim=-1)
    y_pos_2 = y_pre.gather(-1, y_true)
    loss_aux = torch.logsumexp(y_pos_2, dim=-1)
    # 可能需要加一个 clip 操作
    loss_neg = loss_all + torch.log(1 - torch.exp(loss_aux - loss_all))
    return loss_pos + loss_neg


