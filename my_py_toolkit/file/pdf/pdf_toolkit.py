# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from my_py_toolkit.file.file_toolkit import get_file_name, make_path_legal

def split_pdf(pdf_path, save_dir):
  """
  pdf 拆页.
  Args:
    pdf_path:
    save_dir:

  Returns:

  """
  file_name = get_file_name(pdf_path)
  generate_dir = os.path.join(save_dir, file_name)
  if not os.path.exists(generate_dir):
    os.makedirs(generate_dir)
  with open(pdf_path, 'rb') as infile:
    reader = PdfFileReader(infile)
    number_of_pages = reader.getNumPages()  # 计算此PDF文件中的页数
    for i in range(number_of_pages):
      writer = PdfFileWriter()
      writer.addPage(reader.getPage(i))
      out_file_name = generate_dir + str(i + 1) + '.pdf'
      with open(out_file_name, 'wb') as outfile:
        writer.write(outfile)


def extract_pdf_special_pages(pdf_path, save_dir, page_nums):
  """
  提取 pdf 中指定的某些页.
  Args:
    pdf_path:
    save_dir:
    page_nums:

  Returns:

  """
  if not page_nums:
    raise Exception(f"Pages nums can not be empty, cur page_nums:{page_nums}")

  if not os.path.exists(save_dir):
    os.makedirs(save_dir)

  with open(pdf_path, 'rb') as infile:
    reader = PdfFileReader(infile)
    writer = PdfFileWriter()
    for page in page_nums:
      writer.addPage(reader.getPage(page - 1))
    file_name = get_file_name(pdf_path)
    out_file_name = file_name.split(".")[0] + "_" + ",".join([str(page) for page in page_nums]) + ".pdf"
    out_file_path = os.path.join(save_dir, out_file_name)
    with open(out_file_path, "wb") as outfile:
      writer.write(outfile)

