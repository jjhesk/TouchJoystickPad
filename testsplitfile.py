# !/usr/bin/env python
# coding: utf-8
from lib.app import *

if __name__ == '__main__':
    (is_vpn, file_account) = use_args()
    tx = BufferKeyFile()
    tx.new_keyfile()
    tx.read_from("only_bound_ac.txt")
    tx.save_as_split_files(500, file_format="ordzXA{COUNT_INDEX}.txt")
