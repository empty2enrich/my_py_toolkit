# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

from docx import Document

def get_paragraphs(doc_path):
  """
  Gets the text of paragraphs.
  Args:
    doc_path(str): The file path.

  Returns:
    (list(str)): The text of paragraphs.
  """
  doc = Document(doc_path)
  paras = []
  for para in doc.paragraphs:
    paras.append(para.text)
  return paras
