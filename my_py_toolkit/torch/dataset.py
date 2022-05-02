# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3

import random
import torch

from my_py_toolkit.file.file_toolkit import readjson, writejson
from torch.utils.data import IterableDataset

class FileDataset(IterableDataset):
    """
    迭代读取 file 的 dataset, 处理无法全部加载进内存的数据集。
    """
    def __init__(self, paths, shuffle=False, valid_len=4):
        """
        

        Args:
            paths (list(str)): 数据文件路径
            shuffle (bool, optional): 是否 shuffle, IterableDataset 不能使用 Dataloader shuffle. Defaults to False.
            valid_len (int, optional): 需要转换为 torch.Tensor 的数据长度, 数据中并非所有都是输入模型的数据. Defaults to 4.
        """
        super().__init__()
        self.paths = paths
        self.shuffle = shuffle
        self.valid_len = valid_len
        self.size = 0
        for p in self.paths:
            self.size += len(readjson(p)[0])
        
    
    def __iter__(self):
        for p in self.paths:
            datas = readjson(p)
            if self.valid_len > 0:
                datas[:self.valid_len] = [torch.tensor(item, dtype=torch.long) for item in datas[:self.valid_len]]
            idx = list(range(len(datas[0])))
            if self.shuffle:
                random.shuffle(idx)
            for i in idx:
                yield [item[i] for item in datas]

    def __len__(self):
        return self.size