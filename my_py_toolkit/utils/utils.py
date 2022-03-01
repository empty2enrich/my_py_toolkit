# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3


def bit_count(n):
    """
    计算二进制中一的个数
    """
    a = 0
    while a < n:
        n &= n-1
        a += 1
    return a
