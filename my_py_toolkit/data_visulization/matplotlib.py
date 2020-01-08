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

def draw_bar(data, labels, x_label, y_label, title, width=1, interval=1,
             save_path="./test_bar.png"):
  """

  Args:
    data(numpy.object): 二维数据, The size:（context_length, question_length）
    labels(dict): {x_label: [], y_label: []}
    x_label(str):  x 轴标题.
    y_label(str):  y 轴标题.
    title(str): 表标题.
    interval(str): 间隔, 指定两组数据之间的间隔，默认为1，当为 1 的时候， width > 1
    会造成两组数据有重叠，部分被覆盖.

  Returns:

  """
  plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
  matplotlib.rcParams['font.family'] = 'sans-serif'
  plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
  x_tick_labels = labels.get("x_tick_labels", [])
  y_tick_labels = labels.get("y_tick_labels", [])
  # 处理bug：如果 x trick labels 是单个字符与单个标点符号的组合，中文字符只显示一半，加个 “ ” 能处理
  x_tick_labels = [v + " " for v in x_tick_labels]
  y_tick_labels = [v + " " for v in y_tick_labels]

  context_length = len(data)

  rects = []

  fig, ax = plt.subplots()
  x = np.arange(len(x_tick_labels)) * interval

  averge_width = width / context_length
  for index, c_q_attention in enumerate(data):
    rect = ax.bar(x - averge_width * (context_length / 2 - index),
                  c_q_attention,
                  averge_width,
                  label=y_tick_labels[index])
    rects.append(rect)

  ax.set_ylabel(y_label)
  ax.set_xlabel(x_label + "".join(x_tick_labels))
  ax.set_title(title)
  ax.set_xticks(x)
  # 这里可能需要单独指定字体, fontdict={"fontproperties": myfont}，否则输出是乱码,但有时不加也是正常的
  # 第一次脚本需要制定字体，否则输出乱码，但后续使用中，不加也显示正常，不知道为什么？
  # 同时加了字体还导致了其他 bug （汉子单字符只显示左边的一半）
  # 注：此处如果 x trick labels 是单个字符与单个标点符号的组合（在加了 fontdict={"fontproperties": myfont}时），
  # 会导致label 值显示一半，在每个字符后面加个空格可以解决问题
  # ax.set_xticklabels(x_tick_labels, fontdict={"fontproperties": myfont})
  ax.set_xticklabels(x_tick_labels)
  # ax.legend()

  # for rect in rects:
  #   autolabel(rect, ax)
  fig.tight_layout()
  plt.savefig(save_path)


def autolabel(rects, ax):
  """Attach a text label above each bar in *rects*, displaying its height."""
  for rect in rects:
    height = rect.get_height()
    ax.annotate('{}'.format(height),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')


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