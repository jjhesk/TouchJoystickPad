# !/usr/bin/env python
# coding: utf-8
import sys
import time
from typing import Tuple

import tls_client
from lib.com import *
from lib.lib import *

class App(SelfRunner):
    def __init__(self, a: int):
        super().__init__(a)

    # this is the maintenance function
    def loop_point_check(self):
        m = 0
        bbf = BufferKeyFile()
        bbf.new_keyfile()
        while True:
            self.switch_account(m)
            try:
                coins = self.db.get_ordz_coin()
                # x = self.db.is_twitter_account_bind()
                if coins == 0:
                    bbf.add_cmd(self.wallet.reminder)
            except Exception:
                bbf.add_cmd(self.wallet.reminder)

            if m >= self.wallet.account_limit:
                print("DONE ALL ACCOUNTS")
                bbf.save_as("zero_balance.txt")
                bbf.clear()
                break
            m += 1


    def loop_main(self):
        """# loop fighting is now.

        :return:
        """
        m = 0
        finished = False
        while True:
            if m >= self.wallet.account_limit:
                print("DONE ALL ACCOUNTS")
                break
            try:
                self.action_register(code="TOMAISLIVE")
                time.sleep(1)
            except RequestErro:
                print("Have some errors in here..")
                time.sleep(1.5)

            except UnknownErr:
                finished = False
                print("Check from the browser operation for detail")
                print(self.wallet.reminder)
                print("check and see")

            if finished is True:
                self.db.check_point_daily_ops()
                print(">> End game of Today!!")



            time.sleep(1.5)
            m += 1
            self.switch_account(m)

    def skip_check(self):
        if self.db.isFreePlayLimitReached() is True:
            if self.db.check_point_daily_ops_ready() is False:
                raise SkipFromDB()
                # if self.db.is_history_play_confirmed_ready() is False:
                #    raise SkipFromDB()

    def check_play_limit(self):
        # if self.db.isFreePlayLimitReached() is True and self.db.check_point_daily_ops_ready() is True:
        if self.db.isFreePlayLimitReached() is False:
            self.action_today()

            if self.db.isFreePlayLimitReached() is True:
                raise FreePlayLimited()

def use_args(default_key_file: str) -> Tuple[bool, str]:
    is_vpn = False
    file = None
    if len(sys.argv) >= 2:
        is_vpn = sys.argv[1]
        if is_vpn == "p":
            is_vpn = True
        else:
            if ".txt" in is_vpn:
                file = is_vpn
            if ".kz" in is_vpn:
                file = is_vpn
            if ".ks" in is_vpn:
                file = is_vpn
            is_vpn = False

        if len(sys.argv) >= 3:
            file = sys.argv[2]
    if file is None:
        file = default_key_file
    return is_vpn, file
