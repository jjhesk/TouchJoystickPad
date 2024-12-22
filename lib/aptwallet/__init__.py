# !/usr/bin/env python
# coding: utf-8
from .mask import APTOBaseWallet
from .app import AptWallet
import logging

logger1 = logging.getLogger("web3.RequestManager")
logger2 = logging.getLogger("web3.providers.HTTPProvider")
logger3 = logging.getLogger("urllib3.connectionpool")
logger2.setLevel(logging.ERROR)
logger1.setLevel(logging.ERROR)
logger3.setLevel(logging.ERROR)
