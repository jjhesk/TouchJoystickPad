# !/usr/bin/env python
# coding: utf-8
from lib.app import *

if __name__ == '__main__':
    (is_vpn, file_account) = use_args("ordzXA1.txt")
    c = App(0)
    c.port_vpn = 7890 if is_vpn is True else 0
    c.init_from_keyfile(file_account)
    c.loop_main()
