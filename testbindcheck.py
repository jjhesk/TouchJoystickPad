# !/usr/bin/env python
# coding: utf-8
from lib.app import *

if __name__ == '__main__':
    (is_vpn, file_account) = use_args()
    xxtwitter = App(3)
    xxtwitter.port_vpn = 0
    xxtwitter.init_from_keyfile("check_all.txt")
    xxtwitter.loop_check_bind(start_from=0, output_x_binded_account=True)
