# -*- coding: utf-8 -*-
# Copyright .
# Author:
#
# cython: language_level=3
#
import os
import re
import json

def exc_curl(command, content_type="json"):
  """
  命令行执行 curl 命令，并返回数据。
  Args:
    command:
    content_type:

  Returns:

  """
  res = os.popen(command)
  text = res.read()
  res.close()
  data = re.split("\n*|\r*", text)[-1]
  if content_type == "json":
    data = json.loads(data)
  return data

def query_queues(url, user, pwd, v_host=None):
  """
  查询队列。
  Args:
    url:
    user:
    pwd:
    v_host:

  Returns:

  """
  command = ""
  if v_host:
    command = f"curl -i -u {user}:{pwd} {url}/api/queues/{v_host}"
  else:
    command = f"curl -i -u {user}:{pwd} {url}/api/queues"

  queues = exc_curl(command)
  return queues

def query_queues_vhost_names(url, user, pwd, v_host=None):
  """
  查询队列。
  Args:
    url:
    user:
    pwd:
    v_host:

  Returns:

  """
  v_host_name = []
  queues = query_queues(url, user, pwd, v_host)
  for item in queues:
    v_host_name.append((item.get("vhost"), item.get("name")))
  return v_host_name

def purge_queues(url, user, pwd, vhost, queue_name):
  """
  清除队列
  Args:
    url:
    user:
    pwd:
    vhost:
    queue_name:

  Returns:

  """