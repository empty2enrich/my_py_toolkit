# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#
import select
import socket
import errno


def check_conn(self, conn):
  """Check socket connect."""
  to_read, to_write, in_error = select.select([conn], [], [], 0.001)
  if conn in to_read:
    return True
  else:
    return False

def is_socket_valid(self, socket_instance):
  """"""
  if not socket_instance:
    return False
  err_type = None
  try:
    socket_instance.getsockname()
  except socket.error as err:
    err_type = err.args[0]
    if err_type == errno.EBADF:  # 9: Bad file descriptor
      return False

  try:
    socket_instance.getpeername()
  except socket.error as err:
    err_type = err.args[0]
  if err_type in [errno.EBADF, errno.ENOTCONN]:  # 9: Bad file descriptor.
    return False  # 107: Transport endpoint is not connected

  return True