import json

import base58
import requests
import random
import string
from requests import Response

from lib.unisats.bip341 import BIP341Taproot

CHANNEL = ""
VERSION = "1.2.6"
FAIL = "0"
SUCCESS = "1"

UNISAT_WALLET_PRC = "https://wallet-api-testnet.unisat.io"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class RequestConnection:

    def __init__(self, url: str, **kwargs):
        self._base_url = url  # walelt rpc testnet or mainnet
        self.header = {
            'X-Client': 'UniSat Wallet',
            'X-Version': VERSION,
            'x-channel': CHANNEL,
            'x-udid': generate_random_string(12),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-orign",
            "TE": "trailers"
        }

    def header_unisats(self, address: str) -> dict:
        h = self.header
        h.update({
            'x-address': address,
        })
        return h

    def _wrap_base(self, endpoint: str, address: str, method: str = 'GET', data=None) -> Response:
        _url = f'{self._base_url}/{endpoint}'
        y = self.header_unisats(address)
        if method == 'GET':
            if data is None:
                response = requests.get(_url, headers=y)
            else:
                response = requests.get(_url, headers=y, data=data)
        elif method == 'POST':
            y.update({
                'Content-Type': 'application/json;charset=utf-8',
            })
            response = requests.post(_url, headers=y, data=json.dumps(data))
        else:
            raise Exception("[UNISAT][ERROR] unsupported method")
        # print(response.text)
        return response

    def _q(self, endpoint, method='GET', data=None):
        response = self._wrap_base(endpoint, method, data)
        if response.status_code > 300:
            raise Exception(f'[UNISAT][ERROR] Request failed with status code {response.status_code}')
        else:
            if response.status_code == 200:
                kres = response.json()
                if "status" in kres:
                    if kres["status"] == FAIL:
                        if method == 'GET':
                            return {}
                        else:
                            raise Exception(kres["message"])
                    elif kres["status"] == SUCCESS:
                        return kres["result"]
            elif response.status_code == 204:
                return {}
            else:
                return {}
