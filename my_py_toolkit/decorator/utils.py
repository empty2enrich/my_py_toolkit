# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

from functools import partial

def generate_decorator(logger=print, process_fun=None):
  """
  生成修饰器
  Args:
    logger（LogClient）:
    process_fun（func）:

  Examples:
    def fn_timer_process(*args, **kwargs):
      fn = kwargs.pop("fn", None)
      logger = kwargs.pop("logger", None)
      start_time = time.time()
      fn(*args, **kwargs)
      end_time = time.time()
      msg = "Total time running %s: %s seconds" % (
      fn.__name__, str(end_time - start_time))
      if logger:
        logger.info(msg)
      else:
        print(msg)

    @generate_decorator(logger, fn_timer_process)
    def A(a, b, c):
      print("A")

  Returns:
    decorator
  """
  def decorator(fn):
    return partial(process_fun, fn=fn, logger=logger)
  return decorator