# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3


import collections
import re
import unicodedata

from ...basic_data_type.str_toolkit import find_all_index

####################################################################################################
###################################### 文本处理的一些方法 ############################################
####################################################################################################

CHAR_CH_ENG = '\u4e00-\u9fa5a-zA-Z0-9'
CHAR_PUNC = '，,。\.；;‘’“”！!？?：:（）()【】［］《》<>〈〉\[\]\{\}'
REG_CHAR_CH_ENG = f'[{CHAR_CH_ENG}]'
REG_CHAR_PUNC = f'[{CHAR_PUNC}]'


def clean_ch_eng(txt):
    """
    删除 txt 中非中文、英文、数字、标点的字符。

    Args:
        txt (str): 待处理字符串。

    Returns:
        str: 处理后的字符串。
    """
    return re.sub(f'[^{CHAR_CH_ENG}{CHAR_PUNC}]+', '', txt)

def correct_idx(s, sub, idx):
    """
    纠正 idx, 找到与 sub 匹配的最近的 idx。

    Args:
        s (str): 源字符串
        sub (str): 需要查询的子字符串
        idx (int): 原始 idx

    Returns:
        int: 正确的 idx
    """
    most_pro = -1
    for i in find_all_index(s, sub):
        if abs(i - idx) < abs(most_pro - idx):
            most_pro = i
    return most_pro


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
        TODO: 存在bug：
            1、若 token[m], token[m + 1] 在原始 txt 中，两者之间存在 ‘ ’， to_ori_scope(m, m + 1) 会返回 token[m] + 后面 ‘ ’ 在 txt 中的 scope。
            2、若 text 起始位置为 (s, e), 且 text[e] 为 ‘ ’, to_new_scope(s, e) 会返回 text 中(s, e - 1) 的 token。 所以需要保证 e 位置不为空格才能返回正确的范围。
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


def get_sub_scope(txt, subs):
    start = 0
    scopes = []
    for s in subs:
        cur_idx = txt.find(s, start)
        scopes.append((cur_idx, cur_idx + len(s)))
        start = cur_idx + len(s)
    return scopes

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
        contain_white_space(bool): True 表示 text 中包含空格，否则不包含。对 text 与 token idx 映射关系有影响。
            默认情况下， text 中空格是需要删除掉的，但如果text 中包含部分英语单词如：‘here is ...’, 空格能把单词分开，直接去掉空格单词连一起的 
    Return:
        tokens(list(str)): tokenize 后的结果。
        idx_transfer(IdxTransfer): 保存 text 与 token idx 映射关系。
    """
    if not output_idx:
        return tokenizer.tokenize(txt)

    new2ori_idx = []
    ori2new_idx = []
    char_chinese = split_chinese(txt)
    char_scope = get_sub_scope(txt, char_chinese)
    start_idx = 0
    tokens = []
    for char, cur_char_scope in zip(char_chinese, char_scope):
        cur_char_start, cur_char_end = cur_char_scope
        # 两个char 直接可能有空格，导致 idx 不连续。
        # 对于包含英语的内容，我们可能会保留空格，用以区分不同单词，否则连续的单词会连一起。
        # 示例：‘That's because an’, tokenize 出来只有单词，没有空格，导致 token 中字符数与 txt 长度不一致，映射关系也错误。
        #       tokenize 后第二个 token 为 ‘because’, 它的 start_idx 为 7, 不处理会返回了 6, txt[6] 是空格，让 start, end 加一就正常了。
        while start_idx < cur_char_start:
            ori2new_idx.append(len(tokens) - 1)
            start_idx += 1
        start_idx = cur_char_start if start_idx > cur_char_start else start_idx    
        char_token = tokenizer.tokenize(char)
        if len(char) < len(char_token):
            # 存在一个字符被拆分为多个的情况，如：韩文字符
            # todo：这里情况有点不确定，暂时这么写
            for _ in range(start_idx, cur_char_end):
                ori2new_idx.append(len(tokens))
            for c in char_token:
                tokens.append(c)
                new2ori_idx.append((start_idx, cur_char_end))
            start_idx = cur_char_end
        else:
            for cur_idx, c in enumerate(char_token):
                tokens.append(c)
                end_idx = start_idx + len(c)
                if cur_idx > 0 and c.startswith('##'):
                    # -2: 连续数字字母被拆分后，除第一个拆分结果外，后续拆分结果前添加了前缀 '##'
                    end_idx -= 2
                if c in ['[UNK]', '[SEP]']:
                    end_idx -= 4
                    
                # ' \n\t\r' 都转换为 '[PAD]'了，这些 token 不需要
                if c == '[PAD]':
                    print(f'{char} 中 token 出现 [PAD]')
                    new2ori_idx.append((start_idx, start_idx + 1))
                    continue
                
                if start_idx > len(txt) - 1:
                    print(f'idx mapping error: {txt}, token:{c}, start_idx:{start_idx}')
                    # todo: debug
                    break
                
                # end idx 计算可能出错(如：token 出现 [UNK], [PAD], [SEP]等)，加上限制：必须 < cur_char_end
                end_idx = min(end_idx, cur_char_end)        
                new2ori_idx.append((start_idx, end_idx))
                for _ in range(start_idx, end_idx):
                    ori2new_idx.append(len(tokens) - 1)
                start_idx = end_idx
        
            if start_idx > cur_char_end:
                start_idx = cur_char_end
        
    return tokens, IdxTransfer(ori2new_idx, new2ori_idx)

