# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

import signal
import time
from threading import Timer

#################################################################################
################################ 方法运行时间记录 ################################
#################################################################################

def fn_timer(logger=None):
  """
  The decorator for record time.
  The use: @fn_timer(logger) above the definition of method
  Args:
    logger: The logger for record log.

  Returns:
    (function):
  """
  def decorator(fn):
    """
    The decorator for record time.
    Args:
      fn(function): Function that is used by the decorator

    Returns:
      (funtion):
    """
    def running_time_record(*args, **kwargs):
      """
      The method recording time.
      Args:
        *args:
        **kwargs:

      Returns:

      """
      start_time = time.time()
      result = fn(*args, **kwargs)
      end_time = time.time()
      msg = "Total time running %s: %s seconds" % (fn.__name__, str(end_time - start_time))
      if logger:
        logger.info(msg)
      else:
        print(msg)
      return result


    return running_time_record

  return decorator


#################################################################################
################################ 设置方法的超时时间 ################################
##################################################################################

"""
直接设置方法的超时时间

方式一：使用 eventlet (注：针对子进程无法跳出)
import eventlet
eventlet.monkey_patch()
with eventlet.Timeout(2,True):
  time.sleep(3)
  
针对子进程无法跳出：如，一直卡在了 os 模块，不能跳出方法
import time
import eventlet
import os
eventlet.monkey_patch()   #必须加这条代码
with eventlet.Timeout(20,False):   #设置超时时间为20秒
   print '这条语句正常执行'
   cmd1 = 'binwalk -B {0}'.format(filename)
   info1_lines = os.popen(cmd1).readlines()
   cmd2 = 'file {0}'.format(filename)
   info2_lines = os.popen(cmd2).readlines()
   print '没有跳过这条输出'
print '跳过了输出

方式二：func_timeout 模块的@func_set_timeout()
"""

class TimeoutError(Exception):
  pass

def set_timeout(num):
  """
  signal 只能在 Linux 下使用。
  Args:
    num:

  Returns:

  """
  def wrap(func):
    def handle(signum,
               frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
      print(frame)
      raise TimeoutError

    def to_do(*args, **kwargs):
      signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
      signal.alarm(num)  # 设置 num 秒的闹钟
      print('start alarm signal.')
      r = func(*args, **kwargs)
      print('close alarm signal.')
      signal.alarm(0)  # 关闭闹钟
      return r

    return to_do

  return wrap



def time_limit_with_timer(interval):
  """
  使用  Time 设置超时时间。
  注：虽然超时会抛出异常，但不影响方法执行， Timer 是新开的线程几时并抛错，但不能让正在执行的方法退出来。
  Args:
    interval:

  Returns:

  """
  def wraps(func):
    def time_out():
      raise RuntimeError()

    def deco(*args, **kwargs):
      timer = Timer(interval, time_out)
      timer.start()
      res = func(*args, **kwargs)
      timer.cancel()
      return res

    return deco

  return wraps

