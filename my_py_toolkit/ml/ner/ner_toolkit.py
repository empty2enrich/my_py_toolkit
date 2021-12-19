# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3


def update_label_info(txt, label_info, idx_tranf, tag, start_token, end_token):
    """
    更新 label_info.   

    Args:
        txt (str): [description]
        label_info (dict): [description]
        idx_tranf (IdxTransfer): [description]
        tag (str): [description]
        start_token (int): [description]
        end_token (int): [description]

    Returns:
        dict: label info. 
                {'tag': {'entity': [[start, end]]}} , 注：不包含 end.

    """
    # tokens 中补了 '[CLS]' 和 '[SEP]'，所以减一
    start_txt, end_txt = idx_tranf.to_ori_scope(start_token - 1, end_token - 1)
    entity = txt[start_txt: end_txt]
    
    if tag not in label_info:
        label_info[tag] = {}
        
    cur_tag_info = label_info.get(tag, {})
    
    if entity not in cur_tag_info:
        cur_tag_info[entity] = []
    
    cur_entity_info = cur_tag_info.get(entity, [])
    cur_entity_info.append([start_txt, end_txt])
    
    return label_info

def handle_predict(txt, label_pre, idx_tranf):
    """
    根据 ner 模型预测结果，拿到实体。

    Args:
        txt (str): 预测的文本.
        label_pre (list): label 预测结果
        idx_tranf (IdxTransfer): token 与 txt idx 的相互映射类。
        tokens (list): tokens

    Returns:
        dict: 预测结果。
               {'tag': {'entity': [[start, end]]}} , 注：不包含 end. 
    """ 
    label_info = {}
    start = 0
    cur_tag = ''
    is_tag = False
    for i, label in enumerate(label_pre):
        if label.startswith('S-'):
            cur_tag = label[2:].lower()
            update_label_info(txt, label_info, idx_tranf, cur_tag, i, i + 1)
        elif label.startswith('B-'):
            is_tag = True
            start = i
            cur_tag = label[2:].lower()
        elif label.startswith('I-'):
            if not is_tag or label[2:].lower() != cur_tag:
                is_tag = False
        elif label.startswith('E-'):
            if not is_tag or label[2:].lower() != cur_tag:
                is_tag = False
                continue
            update_label_info(txt, label_info, idx_tranf, cur_tag, start, i + 1)
        elif label.startswith('O'):
            is_tag = False

    return label_info