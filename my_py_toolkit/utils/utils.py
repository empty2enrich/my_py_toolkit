# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3
import time

def bit_count(n):
    """
    计算二进制中一的个数
    """
    a = 0
    while a < n:
        n &= n-1
        a += 1
    return a


def get_timestamp(time_str, format="%Y-%m-%d %H:%M:%S"):
    # 先转换为时间数组
    timeArray = time.strptime(time_str, format)
    
    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp