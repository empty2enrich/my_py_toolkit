# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
import numpy as np
from collections import Counter


# def draw_bar(data, labels, x_label, y_label, title, width=1, interval=1,
#              save_path="./test_bar.png"):
#   """
#   这是之前 QA 的时候写的，后续可能用不上，留着用以参考下。
#   Args:
#     data(numpy.object): 二维数据, The size:（context_length, question_length）
#     labels(dict): {x_label: [], y_label: []}
#     x_label(str):  x 轴标题.
#     y_label(str):  y 轴标题.
#     title(str): 表标题.
#     interval(str): 间隔, 指定两组数据之间的间隔，默认为1，当为 1 的时候， width > 1
#     会造成两组数据有重叠，部分被覆盖.

#   Returns:

#   """
#   plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
#   matplotlib.rcParams['font.family'] = 'sans-serif'
#   plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
#   x_tick_labels = labels.get("x_tick_labels", [])
#   y_tick_labels = labels.get("y_tick_labels", [])
#   # 处理bug：如果 x trick labels 是单个字符与单个标点符号的组合，中文字符只显示一半，加个 “ ” 能处理
#   x_tick_labels = [v + " " for v in x_tick_labels]
#   y_tick_labels = [v + " " for v in y_tick_labels]

#   context_length = len(data)

#   rects = []

#   fig, ax = plt.subplots()
#   x = np.arange(len(x_tick_labels)) * interval

#   averge_width = width / context_length
#   for index, c_q_attention in enumerate(data):
#     rect = ax.bar(x - averge_width * (context_length / 2 - index),
#                   c_q_attention,
#                   averge_width,
#                   label=y_tick_labels[index])
#     rects.append(rect)

#   ax.set_ylabel(y_label)
#   ax.set_xlabel(x_label + "".join(x_tick_labels))
#   ax.set_title(title)
#   ax.set_xticks(x)
#   # 这里可能需要单独指定字体, fontdict={"fontproperties": myfont}，否则输出是乱码,但有时不加也是正常的
#   # 第一次脚本需要制定字体，否则输出乱码，但后续使用中，不加也显示正常，不知道为什么？
#   # 同时加了字体还导致了其他 bug （汉子单字符只显示左边的一半）
#   # 注：此处如果 x trick labels 是单个字符与单个标点符号的组合（在加了 fontdict={"fontproperties": myfont}时），
#   # 会导致label 值显示一半，在每个字符后面加个空格可以解决问题
#   # ax.set_xticklabels(x_tick_labels, fontdict={"fontproperties": myfont})
#   ax.set_xticklabels(x_tick_labels)
#   # ax.legend()

#   # for rect in rects:
#   #   autolabel(rect, ax)
#   fig.tight_layout()
#   plt.savefig(save_path)


def autolabel(rects, ax):
  """Attach a text label above each bar in *rects*, displaying its height."""
  for rect in rects:
    height = rect.get_height()
    ax.annotate('{}'.format(height),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')


def draw_bar(y, x_ticks_label=None, y_label=None, width=0.8, title=None, label=None, save_path=None):
  """
  生成条形图。

  Args:
      y ([type]): [description]
      x_ticks_label ([type], optional): [description]. Defaults to None.
      y_label ([type], optional): [description]. Defaults to None.
      width (float, optional): [description]. Defaults to 0.8.
      title ([type], optional): [description]. Defaults to None.
      label ([type], optional): [description]. Defaults to None.
      save_path ([type], optional): [description]. Defaults to None.
  """
  idx = np.arange(len(y))
  fig, ax = plt.subplots()
  p1 = ax.bar(idx, y, width, label=label)

  ax.set_xticks(idx)

  if y_label:
      ax.set_ylabel(y_label)
  if title:
      ax.set_title(title)
  if x_ticks_label:
      ax.set_xticklabels(x_ticks_label)

  ax.legend()

  ax.bar_label(p1, label_type='center')
  if not save_path:
    plt.show()
  else:
    plt.savefig(save_path)


def plot_coh(y, x, y_label=None, x_label=None, title=None, save_path=None):
  """
  画连贯图：x, y 的每对值组成一个坐标，把相邻坐标用线连起来。

  Args:
      y (list(int)): y 轴值，使用数字数组。
      x (list(int)): x 轴值，可使用数字、字母等。
      y_label (str, optional): y 轴标签，说明 y 轴值的含义. Defaults to None.
      x_label (str, optional): x 轴标签，说明 x 轴值含义. Defaults to None.
      title (str, optional): 图的标题. Defaults to None.
      save_path (str, optional): 图的保存路径，若值为空，不保存，直接展示图. Defaults to None.
  """

  _, ax = plt.subplots()
  ax.plot(x, y)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.set_title(title)
  if save_path:
    plt.savefig(save_path)
  else:
    plt.show()


def plot_coh_dict(data, x_label=None, y_label=None, title=None, save_path=None, reverse=False):
  """
  使用 dict 或者 Counter 等数据。

  Args:
      data (dict or Counter): 数据
      x_label (str, optional): x 的 label. Defaults to None.
      y_label (str, optional): y 的自定义名称. Defaults to None.
      title (str, optional): 图的标题. Defaults to None.
      save_path (str, optional): 图的保存路径，无便不保存. Defaults to None.
      reverse (bool or none, optional): bool 表示 data key 的排序方式(key 为数字的情况). Defaults to False.
  """  
  x, y = [], []
  for key, v in sorted(data.items(), key=lambda x: x[0], reverse=reverse):
      x.append(key)
      y.append(v)
  plot_coh(y, x, y_label, x_label, save_path=save_path, title=title)

def draw_bar_dict(data, y_label=None, width=0.8, title=None, label=None, save_path=None, reverse=False):
  """
  使用 dict 或类似的数据画图。

  Args:
      data (dict or Counter): 数据
      y_label (str, optional): y 的label . Defaults to None.
      width (float, optional): 直方图的宽. Defaults to 0.8.
      title (str, optional): 标题. Defaults to None.
      label (str, optional): label. Defaults to None.
      save_path (str, optional): 图的保存路径，无表示不保存. Defaults to None.
  """  
  x, y = [], []
  for key, v in sorted(data.items(), key=lambda x: x[0], reverse=reverse):
      x.append(key)
      y.append(v)
  draw_bar(y, x, y_label, width=width, title=title, label=label, save_path=save_path)

def draw_bar_count(arrs, x_label='cos', y_label='nums of feature'):
    arrs = [round(v, 2) for v in arrs]
    cts = Counter(arrs)
    x, y = [], []
    for k, v in cts.items():
        x.append(k)
        y.append(v)
        
    # plot
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.bar(x, y, width=0.01) #, linewidth=0.01)
    plt.show()
    
def draw_lines(xs, ys, labels, xlabel='', y_label=''):
    fig, ax = plt.subplots()
    for x, y, l in zip(xs, ys, labels):
        ax.plot(x, y, linewidth=2.0, label=l)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(y_label)
    ax.legend()
    plt.show()  
    
    

def test_draw_bar():
  import numpy as np
  # a = list("张三是男是女")
  a = ["张 "] * 5
  a.append("?")
  labels = {

    # "x_tick_labels": ["张三"] * 5,
    "x_tick_labels": a,
    # "x_tick_labels": list("张三是男是女？"),
    "y_tick_labels": list("张三是个30岁男青年。")
  }
  data = np.random.rand(len(labels["y_tick_labels"]),
                        len(labels["x_tick_labels"]))
  x_label = "question_chart"
  y_label = "context_attention"
  title = "Attention"
  width = 0.9
  draw_bar(data, labels, x_label, y_label, title, width)
  pass

if __name__ == "__main__":
  test_draw_bar()