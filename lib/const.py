# !/usr/bin/env python
# coding: utf-8

DATAPATH_BASE = "./cache"
ERROR_COOKIE = "Pls update cookie file"
EVM_RPC = "https://rpc-canary-1.bevm.io"
HERO_API = "https://hero-api.ordz.games"
HOST_API = "https://api.ordz.games"
KEY_FILE_FORMAT = "ordzXA{COUNT_INDEX}.txt"


class VPNConnectionErr(Exception):
    pass


class CookieExpiredErr(Exception):
    pass


class OrdzGame(Exception):
    ...


class RequestErro(Exception):
    ...


class NoActivityToken(OrdzGame):
    ...


class UnboundTwitterErr(OrdzGame):
    ...


class UnknownErr(OrdzGame):
    ...


class FreePlayLimited(OrdzGame):
    ...


class SkipFromDB(OrdzGame):
    ...


class NoSignature(OrdzGame):
    ...


class MemoryErr(OrdzGame):
    ...


class TwitterAccountHasBeenBound(OrdzGame):
    ...

class AccountHasBeenBoundWithTwitter(OrdzGame):
    ...

class InvalidToken(OrdzGame):
    ...


class Rekt(OrdzGame):
    ...


class WalletError(Exception):
    ...


class TokenSessionMissed(OrdzGame):
    ...


class NoReminderNote(WalletError):
    ...


class NoWalletImplemented(WalletError):
    ...


class LocalConf:
    CACHE_PATH: str = "./cache"
    DOM_BASE: str = "./jslab"
    TEMP_FILE: str = "tmp.txt"
    TEMP_JS: str = "tmp.js"
    COOKIE_TMP_FILE: str = "tmp_cookie"
    PUB_KEY: str = "/Users/---/.ssh/id_rsa.pub"
    LOCAL_KEY_HOLDER: str = "/Users/hesdx/.ssh"
    MY_KEY_FEATURE: str = "apple@dapdefi"
    HOME: str = "/root"
    KEY_FILE_FORMAT: str = "zz{COUNT_INDEX}.txt"
    STAGE1 = ["cert", "docker", "env"]
    EVM_RPC = "https://nollie-rpc.skatechain.org"
    NOTE_MEM = "---"
    FIRST_NAME_DICT: list[str] = []
    SURNAME_DICT: list[str] = []
    BEARER = ""
    ORIGIN: str = "https://park.skatechain.org"
    REFERER: str = "https://park.skatechain.org/"
    INVITE_CODE: str = ""
    CURRENT_TWITTER_ID: str = ""
    HOST: str = "park.skatechain.org"
    FAILURE_TO_SHOW_EMAIL: int = 10
    X_FOLLOW_ID: str = '---'
    DATA_SALT: str = "---"
