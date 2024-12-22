# !/usr/bin/env python
# coding: utf-8
from threading import Thread

from lib.twitter import (
    XTwitter,
    TwitterErrorFailure,
    TwitterAccountLocked,
    TwitterPasswordNotFound,
    TwitterUserNotFound,
    TwitterAuthTokenNotFound,
)
# from lib.com.req import UrlReq, MakeHeaders
from lib.sql import TrackerKeep, SqlDataNotFound
from lib.aptwallet import AptWallet
from lib.com import *


class OrdzWrapperThread(Thread):
    def __init__(self, nu: int, prikey: str):
        Thread.__init__(self)
        self.ar = SelfRunner(nu, prikey)

    def setPort(self, p: int = 0):
        self.ar.port_vpn = p

    def debugX(self, b: bool):
        self.ar.debug = b

    def run(self):
        self.ar.one_tick()
        # self.join()


"""
openpyxl
"""


class SelfRunner(UrlReq):
    def __init__(self, process_n: int):
        super().__init__()
        self.process_id = process_n
        self.debug = False
        self.db = TrackerKeep()
        self.wallet = AptWallet()
        self.x = XTwitter()
        self.x.agent = self.agent_x

    def init_from_keyfile(self, filename: str):
        self.wallet.fromKeysFile(filename).fromWalletIndex(0)
        self.db.set_address(self.wallet.address)

    def switch_account(self, x: int):
        self.reset_agent()
        self.wallet.fromWalletIndex(x)
        self.db.set_address(self.wallet.address)
        print(f"=====A/C. [{x}] NOW START FROM {self.wallet.address}")

    def withNote(self, content: str):
        self.wallet.fromMnmenoicPhrase(content)

    def internal_port_vpn(self, k: int):
        self.x.port_vpn = k

    def action_register(self, code: str):
        h = MakeHeaders(
            """          
Host: api-web.tomarket.ai
Connection: keep-alive
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36; BitKeep Android/8.26.1
Content-Type: application/json;charset=UTF-8
Origin: https://newshare.bwb.online
X-Requested-With: com.bgwallet.official
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://newshare.bwb.online/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
"""
        )

        body = {
            "address": self.wallet.address,
            "code": code,
        }

        print(body)
        doc = self.api_action_h(
            "https://api-web.tomarket.ai/tomarket-game/v1/tasks/fillUserBgwAddressForm",
            body,
            h,
        )

        print(doc)


class RunnerThreader(Thread):
    def __init__(self, nu: int, publickey: str):
        Thread.__init__(self)
        self.ar = SelfRunner(nu, publickey)

    def setPort(self, p: int = 0):
        self.ar.port_vpn = p

    def debugX(self, b: bool):
        self.ar.debug = b

    def run(self):
        # self.ar.one_tick()
        # self.join()
        self.start()
