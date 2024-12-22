# !/usr/bin/env python
# coding: utf-8
import random
from binascii import unhexlify
from hdwallet import BIP44HDWallet, BIP32HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from hdwallet.symbols import ETH as SYMBOL
from lib.const import LocalConf


class SolanaWallet:
    reminder: str

    def __init__(self):
        self.reminder = ""

    def from_reminder(self, k: str):
        self.reminder = k

    def from_new_random_private_key(self):
        n = random.randrange(100, 10000)
        wallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet, symbol=SYMBOL)
        wallet.from_mnemonic(mnemonic=LocalConf.NOTE_MEM, language="english", passphrase=None)
        wallet.from_index(n)
        ok_private_key = wallet.private_key()
        print(f"use HD index {n} - private key {ok_private_key}")
        self.from_reminder(ok_private_key)

    def get_seed_array_solana(self):
        wallet: BIP32HDWallet = BIP32HDWallet(cryptocurrency=EthereumMainnet, symbol=SYMBOL)
        wallet.from_mnemonic(mnemonic=self.reminder, language="english", passphrase=None)
        wallet.from_path(path="m/44'/105'/0'/0'")
        return unhexlify(wallet.seed())[0:32]

    @property
    def address_solana(self) -> str:
        return str(self.address_solana_pubkey)

    @property
    def address_solana_pubkey(self) -> Pubkey:
        return self.address_solana_prikey.pubkey()

    @property
    def address_solana_prikey(self) -> Keypair:
        v2 = self.get_seed_array_solana()
        return Keypair.from_seed(v2)
