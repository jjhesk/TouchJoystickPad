# !/usr/bin/env python
# coding: utf-8
import json
import os
import time
from typing import Tuple

import web3

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from eth_account.messages import SignableMessage, encode_defunct
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Aptos
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3 import Web3, middleware
from hdwallet.hds import BIP32HD, BIP44HD
from hdwallet.mnemonics import IMnemonic, BIP39Mnemonic, MONERO_MNEMONIC_WORDS, BIP39_MNEMONIC_LANGUAGES
from hdwallet.derivations import BIP44Derivation
from lib.const import LocalConf, NoReminderNote
from lib.com import (
    read_file_lines,
    read_file_total_lines,
    read_file_at_line,
    read_file_lines_from_encryption,
)


class WalletIdea:
    hd_wallet: HDWallet
    address_list: list[str]
    reminder_list: list[str]
    by_file: bool
    is_key_file: bool
    __addr: str
    pk: str
    file_name: str
    reminder: str
    at_index: int
    account_limit: int
    is_file_encrypted: bool
    w: Web3


class APTOBaseWallet(WalletIdea):

    @property
    def hdd_index(self) -> int:
        return self.at_index

    @property
    def address(self) -> str:
        if isinstance(self.__addr, str):
            return self.__addr
        return ""

    def fromAddressFile(self, file_name: str = "xie.txt"):
        path = os.path.join(LocalConf.CACHE_PATH, file_name)
        self.by_file = True
        self.is_key_file = False
        self.file_name = path
        self.address_list = read_file_lines(path)
        self.account_limit = read_file_total_lines(path)
        return self

    def fromKeysFile(self, file_name: str):
        path = os.path.join(LocalConf.CACHE_PATH, file_name)
        self.file_name = path
        self.by_file = True
        self.is_key_file = True
        return self._read_file_key_phrase(file_name, path)

    def from_key_file_path(self, path: str):
        fl, file_name = os.path.split(path)
        self.file_name = path
        self.by_file = True
        self.is_key_file = True
        return self._read_file_key_phrase(file_name, path)

    def _read_file_key_phrase(self, file: str, file_name_path: str):
        if ".kz" in file or ".ks" in file:
            self.is_file_encrypted = True
            note_list = read_file_lines_from_encryption(file_name_path)
            self.address_list = self._address_in_list_by_file(note_list)
            self.account_limit = len(self.address_list)
        else:
            self.is_file_encrypted = False
            note_list = read_file_lines(file_name_path)
            self.address_list = self._address_in_list_by_file(note_list)
            self.account_limit = read_file_total_lines(file_name_path)
        self.reminder_list = note_list
        return self

    def fromMnmenoicPhrase(self, content_text: str):
        self.reminder = content_text
        self.by_file = False
        self.file_name = ""
        short = f"{content_text[:8]}...{content_text[len(content_text) - 8:]}"
        print(f"wallet is now using HD with one single phrase {short}")
        return self

    def ercwallet_init__uni(self):
        self.reminder = "..."
        self.__addr = ""
        self.by_file = False
        self.is_key_file = False
        self.file_name = ""
        self.address_list = []
        self.account_limit = 0
        self.at_index = 0
        self.w = Web3(Web3.HTTPProvider(LocalConf.EVM_RPC))
        self.w.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.w.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w.middleware_onion.add(middleware.simple_cache_middleware)

    def _address_in_list_by_file(self, notes: list) -> list:
        f = []
        for note in notes:
            (addr, _) = self._apt_gen_address(note, 0)
            f.append(addr)
        return f

    def fromWalletIndex(self, n: int):
        if self.by_file is False:
            if self.reminder == "...":
                raise NoReminderNote()
            self.at_index = n
            (address, _private) = self._apt_gen_address(self.reminder, n)
            self.__addr = address
            self.pk = _private
        else:
            if self.is_key_file is True:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = self.reminder_list[k]
                (address, _private) = self._apt_gen_address(self.reminder, 0)
                self.__addr = address
                self.pk = _private
            else:
                k = n % self.account_limit
                self.at_index = k
                self.reminder = "..."
                self.__addr = read_file_at_line(self.file_name, k)
                self.pk = ""

    def _apt_gen_address(self, mnemonic: str, at_index: int = 0) -> Tuple[str, str]:
        try:
            wacoin: HDWallet = HDWallet(
                cryptocurrency=Aptos,
                hd=BIP44HD,
                network=Aptos.DEFAULT_NETWORK
            )
            note = BIP39Mnemonic(
                mnemonic=mnemonic
            )
            wacoin.from_mnemonic(mnemonic=note)
            apt_address = wacoin.address()
            main_pk = wacoin.private_key()
            self.hd_wallet = wacoin
            return (apt_address, main_pk)
        except ValueError as e:
            print("error on taproot creation")
            return ("", "")

    def is_ready(self) -> bool:
        return self.pk != ""

    def from_private_key(self, k: str):
        PA = self.w.eth.account.from_key(k)
        self.pk = k
        self.__addr = PA.address

    def in_asset(self, detect_balance: float) -> bool:
        address = Web3.to_checksum_address(self.address)
        bal = self.w.eth.get_balance(address)
        save = detect_balance * 10 ** 18
        return bal > save

    def sweep_asset(self, nft: str, nft_id: int, next_address: str):
        # sweep NFT
        safe_transfer = "0x42842e0e"
        from_address = self.input_addr_code(self.address)
        to_address = self.input_addr_code(next_address)
        token_id = self.input_integer_code(nft_id)
        hex_data = f"{safe_transfer}{from_address}{to_address}{token_id}"
        self._transaction(nft, hex_data)
        # sweep balance

    def sweep_balance(self, small_balance: float, next_address: str):
        gas = 210000
        gas_price = self.w.eth.gas_price
        # gas_price = 10008
        address = Web3.to_checksum_address(self.address)
        bal = self.w.eth.get_balance(address)
        save = small_balance * 10 ** 18
        # balance_after_fee = bal
        # balance_after_fee = bal - int(save)
        # balance_after_fee = bal - int(gas) * gas_price
        balance_after_fee = bal - int(save)
        # print(f"save wei {int(save)}")
        # print(f"balance save {bal} - {int(save)} = {balance_after_fee}, gas:{gas}, gas price:{gas_price}")
        # print(f"balance save {balance_after_fee}, gas:{gas}, gas price:{gas_price}")
        # print(f"gas * price + value = {gas} x {gas_price} + {balance_after_fee} = {bal}")
        if balance_after_fee <= 0:
            print(
                f"Please add fund to the account {self.address} in order to sweep balance"
            )
            return

        # next_address = Web3.to_checksum_address(next_address)
        # nonce = self.w.eth.get_transaction_count(address)
        nonce = self.w.eth.get_transaction_count(address, "pending")

        transaction = {
            "nonce": nonce,
            "to": next_address,
            "from": self.address,
            "value": balance_after_fee,
            "gasPrice": gas_price,
            "gas": gas,
        }
        signed_txn = self.w.eth.account.sign_transaction(transaction, self.pk)
        tx_hash = self.w.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction Hash: {self.w.to_hex(tx_hash)}")
        ok = self.w.eth.wait_for_transaction_receipt(tx_hash, 5)
        print(f"Transaction Confirmed: {ok}")

    def input_integer_code(self, id: int):
        return hex(id)[2:].zfill(64)

    def input_addr_code(self, address: str):
        return address.lower()[2:].zfill(64)

    def _transaction(self, contract, hex_data):
        try:
            self._tx(contract, hex_data)
        except web3.exceptions.TimeExhausted as timeout:
            print("time out after 10s its okay. lets it be..", timeout)
        except ValueError as e:
            if "nonce too low" in str(e):
                print("retry... nonce too low")
                time.sleep(3)
                self._tx(contract, hex_data)
            else:
                print(e)
                exit(0)

    def _tx(self, contract, hex_data):
        address = Web3.to_checksum_address(self.address)
        self.nonce = self.w.eth.get_transaction_count(address)
        transaction = {
            "nonce": self.nonce,
            "to": contract,
            "value": 0,  # Amount of ETH to send (in Wei)
            "gas": 2000000,  # Adjust gas limit as needed
            "gasPrice": self.w.eth.gas_price,
            "data": hex_data,
            "chainId": self.w.eth.chain_id,
        }
        signed_txn = self.w.eth.account.sign_transaction(transaction, self.pk)
        tx_hash = self.w.eth.send_raw_transaction(signed_txn.rawTransaction)
        # print(f"Transaction Hash: {self.w.to_hex(tx_hash)}")
        ok = self.w.eth.wait_for_transaction_receipt(tx_hash, 10)
        print(f"Transaction Confirmed: {ok}")
