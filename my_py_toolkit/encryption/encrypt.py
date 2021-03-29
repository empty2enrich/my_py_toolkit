# -*- coding: utf-8 -*-
# Copyright 2019 Huairuo.ai.
# Author: Lin Li (li.lin@huairuo.ai)
#
# cython: language_level=3
#

import hashlib

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def sha1prng(seed, bit_size=128):
  """
  sha1prng 实现, 结果长度为 bit_size/8, 默认 16。
  Args:
    seed(str):
    bit_size(int):

  Returns:

  """
  return hashlib.sha1(hashlib.sha1(seed.encode()).digest()).digest()[:bit_size//8]


def encrypt_aes_sha1prng_ecb(content, key_seed):
  """
  使用 sha1prng、AES 的 ecb mode 加密。
  Args:
    content(str): 需要加密的内容。
    key_seed(str): sha1prng加密生成 key 的 seed。

  Returns:
    (str): 加密后内容。
  """
  key = sha1prng(key_seed)
  cipher = AES.new(key, AES.MODE_ECB)
  ct_bytes = cipher.encrypt(pad(content.encode(), AES.block_size))
  return b64encode(ct_bytes).decode("utf-8")

def decrypt_aes_sha1prng_ecb(encrypted_content, key_seed):
  """
  使用 sha1prng、AES 的 ecb mode 解密。
  Args:
    encrypted_content(str): 加密后的内容。
    key_seed(str): sha1prng加密生成 key 的 seed。
  Returns:
    (str):
  """
  key = sha1prng(key_seed)
  ct = b64decode(encrypted_content)
  cipher = AES.new(key, AES.MODE_ECB)
  pt = unpad(cipher.decrypt(ct), AES.block_size)
  return pt.decode('utf-8')


if __name__ == "__main__":
  pass
