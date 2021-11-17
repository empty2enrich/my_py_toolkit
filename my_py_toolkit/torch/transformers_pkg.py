# -*- encoding: utf-8 -*-
#
# Author: LL
#
# transformers 包的使用
# 
# cython: language_level=3


from transformers.modeling_bert import BertConfig, BertModel
from transformers.tokenization_bert import BertTokenizer

####################################################################################################
###################################### BERT ############################################
####################################################################################################

def bert_tokenize(bert_cfg):
    """
    加载 bert tokenizer

    Args:
        bert_cfg (str): tokenizer 配置信息。
            1、若初始化一个新的 BERT 模型， bert_cfg 为 bert config.json 路径；
            2、若加载训练好的 BERT, bert_cfg 为 bert 模型所在文件夹路径
    """
    return BertTokenizer.from_pretrained(bert_cfg)
    

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
  model = None
  if use_pretrained:
    model = BertModel.from_pretrained(bert_cfg).to(device)
  else:
    model = BertModel(BertConfig(bert_cfg)).to(device)
  
  if freeze_params:
    for param in model.parameters():
      param.requires_grad = False
  
  return model