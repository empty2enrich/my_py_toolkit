# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

########
# 默认日期格式, eg: 2021-01-01 12:12:12.123
default_date_format = "%Y-%m-%d %H:%M:%S.%f"

from datetime import datetime, date

# 秒与其他时间单位换算表
SECONDS_CONV_TABLE = {
  "year": 365 * 24 * 3600,
  "month": 30 * 24 * 3600,
  "day": 24 * 3600,
  "hour": 3600,
  "minute": 60,
  "second": 1
}

def str2time(time_str, format=default_date_format):
  """
  日期格式化。
  Args:
    time_str(str): 日期字符串。
    format(str): 日期格式。

  Returns:
    (datetime.datetime):
  """
  return datetime.strptime(time_str, format)

def time_defference(time_1, time_2, time_format=default_date_format, unit="second"):
  """
  计算两个时间的间隔，unit 控制返回值的单位：年月日时分秒。
  Args:
    time_1(str): 日期字符串
    time_2(str): 日期字符串
    unit(str): year(年), month(月), day(天), hour(小时), minute(分), second(秒)。

  Returns:
    (float):
  """
  seconds = (str2time(time_1, time_format) - str2time(time_2, time_format)).total_seconds()
  seconds = abs(seconds)
  return seconds/SECONDS_CONV_TABLE.get(unit, 1)

if __name__ == "__main__":
  # print(time_defference(t_1, t_2))
  time_1 = "2021-01-03 12:12:12.123"
  time_2 = "2021-01-02 12:32:12.123"
  t_d = str2time(time_1) - str2time(time_2)
  print(time_defference(time_1, time_2, unit="day"))