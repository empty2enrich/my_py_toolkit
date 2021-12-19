# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3


import collections
import re
import unicodedata

class Vocab():
    """
    生成词汇表。id 与 token 能互相转换。
    """
    def __init__(self, tokens, min_times=0, reserved_token=[]):
        if len(tokens) == 0 or isinstance(tokens[0], list):
            tokens = [t for line in tokens for t in line]
        counter = collections.Counter(tokens)
        self.corpus = sorted(counter.items(), key = lambda x:x[1], reverse=True)
        self.idx2token, self.token2idx = [], {}
        self.unk  = 0 
        unique_token = ['unk'] + reserved_token if reserved_token is not None else []
        for char, _ in self.corpus:
            if char not in unique_token and _ >= min_times:
                unique_token.append(char)
        for char in unique_token:
            self.idx2token.append(char)
            self.token2idx[char] = len(self.idx2token) - 1
        self.vocab_size = len(unique_token)

    def __len__(self):
        return self.vocab_size

    def __getitem__(self, tokens):
        if not isinstance(tokens, (list, tuple)):
            return self.token2idx.get(tokens, self.unk)
        return [ self.__getitem__(t) for t in tokens]
    
    def to_token(self, indices):
        if not isinstance(indices, (list, tuple)):
            return self.idx2token[indices]
        return [self.idx2token[i] for i in indices]

####################################################################################################
###################################### Tokenize ############################################
####################################################################################################

class IdxTransfer(object):
    """
    idx 转换。

    新旧 idx 转换, 新的 idx 一个可能对应多个旧 idx。旧 idx 只对应一个新 idx。
    """
    def __init__(self, ori2new_idx, new2ori_idx):
        """
        

        Args:
            ori2new_idx (list(int)): 原始 idx 与新 idx 的映射关系。
            new2ori_idx (list((start, end))): 新 idx 与原始 idx 映射关系, 新的 idx 一个可能对于多个原始 ori, 从 start 到 end, 不包含 end。
        """
        self.ori2new_idx = ori2new_idx
        self.new2ori_idx = new2ori_idx
        
      
    def to_new(self, ori_idx):
        """
        将原始 idx 转换为 token idx。
        注：多个原始 idx 可能对应同一个 token idx, 需要考虑 idx 越界情况。

        Args:
            ori_idx (int): 原始 idx。

        Returns:
            int: token idx。
        """
        if ori_idx < len(self.ori2new_idx):
            return self.ori2new_idx[ori_idx]
        else:
            return len(self.new2ori_idx)
    
    def to_ori(self, new_idx):
        if new_idx < len(self.new2ori_idx):
            return self.new2ori_idx[new_idx][0]
        else:
            return len(self.ori2new_idx)


    def to_new_scope(self, start, end):
        """
        将原始 idx 转换为 token idx。
        注：多个原始 idx 可能对应同一个 token idx, 需要考虑 idx 越界情况。

        Args:
            start (int): 原始 idx 起始位置。
            end (int): 原始 idx 结束位置。(不包含 end 位置)

        Returns:
            int: token idx。
        """
        return [self.to_new(start), self.to_new(end)]
    
    def to_ori_scope(self, start, end):
        """
        将 token idx 转换为原始 idx。
        
        args:
            start (int): token idx 起始位置。
            end (int): token idx 结束位置。(不包含 end 位置)
        """
        return [self.to_ori(start), self.to_ori(end)]

def _tokenize_chinese_chars(text):
    """Adds whitespace around any CJK character."""
    output = []
    for char in text:
        cp = ord(char)
        if _is_chinese_char(cp) or _is_punctuation(char):
            output.append(" ")
            output.append(char)
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)

def _is_punctuation(char):
    """Checks whether `chars` is a punctuation character."""
    cp = ord(char)
    # We treat all non-letter/number ASCII as punctuation.
    # Characters such as "^", "$", and "`" are not in the Unicode
    # Punctuation class but we treat them as punctuation anyways, for
    # consistency.
    if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
            (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
        return True
    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False

def _is_chinese_char(cp):
    """Checks whether CP is the codepoint of a CJK character."""
    # This defines a "chinese character" as anything in the CJK Unicode block:
    #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
    #
    # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
    # despite its name. The modern Korean Hangul alphabet is a different block,
    # as is Japanese Hiragana and Katakana. Those alphabets are used to write
    # space-separated words, so they are not treated specially and handled
    # like the all of the other languages.
    if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
            (cp >= 0x3400 and cp <= 0x4DBF) or  #
            (cp >= 0x20000 and cp <= 0x2A6DF) or  #
            (cp >= 0x2A700 and cp <= 0x2B73F) or  #
            (cp >= 0x2B740 and cp <= 0x2B81F) or  #
            (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or  #
            (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
        return True

    return False

def split_chinese(txt):
    """
    将中文字符串分割：
      1、汉字按字拆开
      2、连续的字母数字作为一个整体。

    示例：‘今天wefw234威风’ -> ['今', '天', 'wefw234', '威', '风']

    Args:
        txt (str): 待分割字符串。
    """
    txt = _tokenize_chinese_chars(txt)
    return re.split(' +', txt.strip())


def tokenize_chinese(tokenizer, txt, output_idx=False):
    """
    对中文文本进行 tokenize.

    作用：
        1、为了把 token 映射回原 text 所在 idx: 对于中文中的连续字母、数字, tokenize 后每个结果可能都由多个字符组成，
    同时 tokenize 后结果有添加前缀 '##', 字符数变多，与原位置对于不上
        2、token 与原位置对于上后，才能处理数据的 label, 否则对于不上。

    Args:
        tokenizer ([type]): Tokenizer, 用于字符串 tokenize 的类。
        txt (str): 待 tokenize 的文本。
        output_idx(bool): True 表示返回 token 与原文本的 idx 映射关系，否则不返回。
    
    Return:
        tokens(list(str)): tokenize 后的结果。
        new2ori_idx(list((start, end))): 当前 tokens 在原 txt 的对应位置, 
            对于(start, end), 不包含 end 位置。
        ori2new_idx(list(int)): 原文本中 idx 字符在 tokens 中的对应位置。
    """
    if not output_idx:
        return tokenizer.tokenize(txt)

    new2ori_idx = []
    ori2new_idx = []
    char_chinese = split_chinese(txt)
    start_idx = 0
    tokens = []
    for char in char_chinese:
        for cur_idx, c in  enumerate(tokenizer.tokenize(char)):
            tokens.append(c)
            end_idx = start_idx + len(c)
            if cur_idx > 0 and c.startswith('##'):
                # -2: 连续数字字母被拆分后，除第一个拆分结果外，后续拆分结果前添加了前缀 '##'
                end_idx -= 2
            if c == '[UNK]':
                end_idx -= 4
            new2ori_idx.append((start_idx, end_idx))
            for _ in range(start_idx, end_idx):
                ori2new_idx.append(len(tokens) - 1)
            start_idx = end_idx
        
    return tokens, IdxTransfer(ori2new_idx, new2ori_idx)
