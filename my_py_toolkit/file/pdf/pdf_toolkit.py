# -*- coding: utf-8 -*-
# Copyright 2019
# Author:
#
# cython: language_level=3
#

import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from my_py_toolkit.file.file_toolkit import get_file_name

def split_pdf(pdf_path, save_dir):
  """"""
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