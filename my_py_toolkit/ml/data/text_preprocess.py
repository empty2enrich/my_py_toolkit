# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3

import collections


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