# ----
# !/usr/bin/env python
# coding: utf-8
import random
import secrets
import string
from datetime import datetime, timedelta
from typing import Tuple
from eth_account.messages import SignableMessage, encode_defunct
from .mask import APTOBaseWallet
from ..com.util import BufferKeyFile


def generate_nonce(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_timestamp():
    # Get the current datetime in UTC
    ct1 = datetime.utcnow()
    ct2 = ct1 + timedelta(seconds=10)

    # Format the datetime as per the required format
    issue = ct1.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    expire = ct2.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return issue, expire


def random_string_for_entropy(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


SIGN_MESSAGE = """galxe.com wants you to sign in with your Ethereum account:
{ADDRESS_HERE}

Sign in with Ethereum to the app.

URI: https://galxe.com
Version: 1
Chain ID: 137
Nonce: {NONCE}
Issued At: {T1}
Expiration Time: {T2}"""
KYC_MESSAGE = """get_or_create_address_inquiry:{ADDRESS_HERE}"""


class AptWallet(APTOBaseWallet):
    backup: BufferKeyFile

    def __init__(self):
        self.ercwallet_init__uni()

    def init_newfile_reminder(self, default_name:str, format_name:str,  index: int = -1):
        """
        default_name: the default back up file name without format parameter
        format_name: the format name to add for index with parameter in the middle
        """
        self.backup = BufferKeyFile()
        if index == -1:
            self.backup.new_keyfile(default_name)
        else:
            self.backup.new_keyfile(format_name.format(INDEX=index))

    def keep_reminder(self):
        self.backup.add_reminder(self.reminder)

    def reminder_tmp_close(self):
        self.backup.reminder_consolidate()

    def action_collect_treasure(self, adventure_contract: str):
        if self.pk == "":
            print("no private key is setup")
            return ""
        hex_data = "0x9b7d30dd0000000000000000000000000000000000000000000000000000000000000001"
        self._transaction(adventure_contract, hex_data)

    def action_adventure(self, adventure_contract: str):
        hex_data = "0x9b7d30dd0000000000000000000000000000000000000000000000000000000000000002"
        self._transaction(adventure_contract, hex_data)

    def sign_message_test_genesis(self, msg: str) -> Tuple[str, dict]:
        ss: SignableMessage = encode_defunct(text=msg)
        # ke = "9260c0e179d0c1aaf760eecfbbbb4b8baddb919b1e06e702e45490319fad6b14"
        signature = self.w.eth.account.sign_message(ss, self.pk)
        # signature = self.w.eth.account.sign_message(ss, ke)
        signature_text = signature.signature.hex()
        data_ver = {
            "version": "1",
            "msg": msg,
            "sig": signature_text,
            "address": self.address
        }
        # print("double check on @ https://app.mycrypto.com/verify-message")
        # print(data_ver)
        return signature_text, data_ver

    def sign_galxe_msg(self) -> Tuple[str, str]:
        (t1, t2) = generate_timestamp()
        nonce = random_string_for_entropy(17)
        msg = SIGN_MESSAGE.format(
            NONCE=nonce,
            ADDRESS_HERE=self.address,
            T1=t1,
            T2=t2,
        )
        # sample="event.genomefi.io wants you to sign in with your Ethereum account:0x10680C492cC85C6B79062D13f4251FfA7dd10272Sign in GenomeFi.URI: https://event.genomefi.ioVersion: 1Chain ID: 137Nonce: HoUHOzb72LLSwL5DiIssued At: 2024-03-20T06:33:00.798ZExpiration Time: 2024-03-20T06:43:00.795Z"
        (signature, d) = self.sign_message_test_genesis(msg)
        return msg, signature

    def sign_galxe_kyc_msg(self) -> Tuple[str, str]:
        msg = KYC_MESSAGE.format(
            ADDRESS_HERE=self.address.lower(),
        )
        (signature, d) = self.sign_message_test_genesis(msg)
        return msg, signature
