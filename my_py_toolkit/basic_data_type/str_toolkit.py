# -*- encoding: utf-8 -*-
#
# Author: LL
#
# cython: language_level=3



def find_all_index(s, sub):
    """
    找到字串所有出现位置。

    Args:
        s (str): 源字符串
        sub (str): 需要查询的子字符串

    Yields:
        generatpr: 返回所有出现位置的迭代器
    """
    start = 0
    while True:
        start = s.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)

def longest_common_sub_str(text1, text2):
    """
    求出 text1, text2 的最长公共子序列长度。

    Args:
        text1 (str): 字符串
        text2 (str): 字符串
    """
    m, n = len(text1), len(text2)
    pre, cur = [0] * (n + 1), [0] * (n + 1)
    max_len = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                cur[j] = pre[j - 1] + 1
            else:
                cur[j] = max(pre[j], cur[j-1])
            max_len = max(max_len, cur[j])
        pre = cur
        cur = [0] * (n + 1)
    return max_len
