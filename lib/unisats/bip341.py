# !/usr/bin/env python
# coding: utf-8

import os

from typing import Tuple

import requests
from bitcointx.signmessage import BitcoinMessage, SignMessage
from bitcointx.wallet import CBitcoinExtKey, P2TRCoinAddress, P2TRBitcoinAddress, CBitcoinSecret
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import BitcoinMainnet as Cryptocurrency
from ..const import DATAPATH_BASE, NoReminderNote, NoWalletImplemented


def read_file_lines(filename: str) -> list:
    content_line = []
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            tmp = content.strip().replace("\n", "")
            content_line.append(tmp)
        fp.close()
    return content_line


def read_file_at_line(filename: str, line: int) -> str:
    content_line = ""
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            if count == line:
                content_line = content.strip().replace("\n", "")
        fp.close()
    return content_line


def read_file_total_lines(filename: str) -> int:
    print(f"count lines from bip341 {filename}")
    with open(filename, 'r') as fp:
        for count, line in enumerate(fp):
            pass
        fp.close()
    print('Total Lines', count + 1)
    return count + 1


class BIP341Taproot:
    hd_wallet: BIP44HDWallet
    address_list: list[str]
    by_file: bool
    is_key_file: bool
    __addr: str
    file_name: str
    reminder: str
    at_index: int
    account_limit: int

    def fromAddressFile(self, file_name: str = "xie.txt"):
        path = os.path.join(DATAPATH_BASE, file_name)
        self.by_file = True
        self.is_key_file = False
        self.file_name = path
        self.address_list = read_file_lines(path)
        self.account_limit = read_file_total_lines(path)
        return self

    def fromKeysFile(self, file_name: str = "ordz.02.txt"):
        path = os.path.join(DATAPATH_BASE, file_name)
        self.file_name = path
        self.by_file = True
        self.is_key_file = True
        note_list = read_file_lines(path)
        self.address_list = self._address_in_list_by_file(note_list)
        self.account_limit = read_file_total_lines(path)
        return self

    def fromMnmenoicPhrase(self, content_text: str):
        self.reminder = content_text
        self.by_file = False
        self.file_name = ""
        short = f"{content_text[:8]}...{content_text[len(content_text) - 8:]}"
        print(f"wallet is now using HD with one single phrase {short}")
        return self

    def unsats__init__uni(self):
        self.reminder = "..."
        self.__addr = ""
        self.by_file = False
        self.is_key_file = False
        self.file_name = ""
        self.address_list = []
        self.account_limit = 0
        self.at_index = 0

    @property
    def hdd_index(self) -> int:
        return self.at_index

    @property
    def address(self) -> str:
        if isinstance(self.__addr, P2TRBitcoinAddress):
            return str(self.__addr)
        if isinstance(self.__addr, str):
            return self.__addr
        return ""

    @property
    def wif(self) -> str:
        # the compressed private key
        if self.hd_wallet is None:
            print("the HD wallet is not setup")
            raise NoWalletImplemented()
        return self.hd_wallet.wif()

    def _taproot_address(self, mnemonic: str, at_index: int = 0) -> Tuple[str, str, str]:
        try:
            # print(mnemonic)
            # print("test key note:")
            # print(mnemonic)
            bwl: BIP44HDWallet = BIP44HDWallet(
                cryptocurrency=Cryptocurrency, account=0, change=False, address=0
            )
            bwl.from_mnemonic(mnemonic, language="english", passphrase=None)
            bwl.clean_derivation()
            bwl.from_path("m/86'/0'/0'/0")
            bwl.from_index(at_index)
            linking_key = bwl.public_key()
            tap_root_extend_private_key = bwl.xprivate_key()
            key = CBitcoinExtKey(tap_root_extend_private_key)
            p2tr_address = P2TRCoinAddress.from_xonly_pubkey(key.pub)
            wif = bwl.wif()
            self.hd_wallet = bwl
            return (p2tr_address, linking_key, wif)
        except ValueError as e:
            print("error on taproot creation")
            return ("", "", "")

    def okx_sign_message(self, message: str) -> str:
        secret_wif = self.hd_wallet.wif()
        sec = CBitcoinSecret(secret_wif)
        sign_message = BitcoinMessage(message)
        signature = SignMessage(sec, sign_message)
        return signature.decode("utf-8")

    def _address_in_list_by_file(self, notes: list) -> list:
        f = []
        for note in notes:
            (p2tr_address, _, _) = self._taproot_address(note, 0)
            f.append(p2tr_address)
        return f

    def fromWalletIndex(self, n: int):
        if self.by_file is False:
            if self.reminder == "...":
                raise NoReminderNote()
            self.at_index = n
            (p2tr_address, link, f) = self._taproot_address(self.reminder, n)
            self.__addr = p2tr_address
            self.link = link
        else:
            if self.is_key_file is True:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = read_file_at_line(self.file_name, k)
                (p2tr_address, link, f) = self._taproot_address(self.reminder, 0)
                self.__addr = p2tr_address
                self.link = link
            else:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = "..."
                self.__addr = read_file_at_line(self.file_name, k)
                self.link = ""

    def checkBalanceTestnet(self) -> int:
        # external checking for btc balance on testnet.
        value = 0
        with requests.get(f"https://mempool.space/testnet/api/address/{self.address}/txs", headers={
            "Referer": f"https://mempool.space/testnet/address/{self.address}",
            "Host": "mempool.space",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-orign",
            "TE": "trailers",
            "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        }) as c:
            if c.status_code != 200:
                return 0
            # print(c.json())
            if isinstance(c.json(), list):
                for tx in c.json():
                    for batch in tx["vout"]:
                        if "scriptpubkey_address" in batch:
                            address = batch["scriptpubkey_address"]
                            if str(address).lower() == str(self.__addr).lower():
                                value += int(batch["value"])
        return value
