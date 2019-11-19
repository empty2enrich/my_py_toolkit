# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

import time

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