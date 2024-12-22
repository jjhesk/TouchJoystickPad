# !/usr/bin/env python
# coding: utf-8
import json
import os
import time
from typing import Optional

from lib.const import *
from .solver02 import OrdzSolverLib
from .util import RandomAgentClass

try:
    import tls_client
except:
    os.system("python -m pip install tls-client")
    import tls_client


def MakeHeaders(plain_text: str) -> dict:
    # 将HTTP头信息分割成单独的行
    headers_list = plain_text.strip().split("\n")
    # 创建一个空字典来存储HTTP头信息
    headers_dict = {}
    # 遍历每一行，将其添加到字典中
    for header in headers_list:
        key, value = header.split(": ", 1)
        headers_dict[key] = value
    # 将字典转换为JSON格式
    # headers_json = json.dumps(headers_dict, indent=4)
    return headers_dict


class UrlReq:
    agent_x: str
    session: tls_client.Session

    def __init__(self):
        self.reset_agent()
        self.cookie_use = False
        self.port_vpn = 7890
        self.token_session = ""
        self.decode = OrdzSolverLib()

    def reset_agent(self):
        self.agent_x = RandomAgentClass.randomagent()
        self.session = tls_client.Session(
            client_identifier="firefox_104",
            supported_signature_algorithms=[
                "ECDSAWithSHA256",
                "SHA256",
                "SHA384",
                "SHA512",
                "SHA256WithRSAEncryption",
                "SHA384WithRSAEncryption",
                "SHA512WithRSAEncryption",
                "ECDSAWithSHA384",
            ],
            supported_versions=["GREASE", "1.3", "1.2"],
            key_share_curves=["GREASE", "X25519"],
            cert_compression_algo="brotli",
            pseudo_header_order=[":method", ":authority", ":scheme", ":path"],
            connection_flow=15663105,
            header_order=["accept", "user-agent", "accept-encoding", "accept-language"],
        )

    @property
    def port_vpn(self) -> int:
        """I'm the 'x' property."""
        return self._port_vpn

    @port_vpn.setter
    def port_vpn(self, value: int):
        self._port_vpn = value
        if value > 0:
            self.session.proxies = {
                "http": f"http://127.0.0.1:{value}",
                "https": f"http://127.0.0.1:{value}",
            }
        else:
            self.session.proxies = None
            self.internal_port_vpn(value)

    def internal_port_vpn(self, k: int):
        pass

    def useManualCookie(self):
        self.cookie_use = True

    def load_page(self, h, r, save_res: bool = True) -> bool:
        response = self.session.get(
            h, headers=self.header_doc_ref(r), allow_redirects=True
        )
        if response.status_code == 200:
            if save_res is True:
                self.decode.external_save_content(response.content)
            return True
        else:
            # print(response.status_code)
            return False

    def api_action_bool_res(self, p: str, q: dict) -> bool:
        return self.api_action_h(p, q, self.hloginsession(), self.res_boolean_handle)

    def pre_header(self) -> dict:
        y = self.gen_header()
        y.update(
            {
                "Access-Control-Request-Headers": "content-type",
                "Access-Control-Request-Method": "POST",
            }
        )
        return y

    def hloginsession(self) -> dict:
        if self.token_session is None or self.token_session == "":
            raise TokenSessionMissed("token session is not found")
        header_ingame = self._header_in_game()
        header_ingame.update({"ordz-session": self.token_session})
        return header_ingame

    def sessionFromUser(self, token_session: str) -> dict:
        header_ingame = self._header_in_game()
        header_ingame.update({"ordz-session": token_session})
        return header_ingame

    def loginfix(self) -> dict:
        if self.token_session is None or self.token_session == "":
            raise TokenSessionMissed("token session is not found")
        j = self.gen_header()
        j.update({"ordz-session": self.token_session})
        return j

    def gen_header(self) -> dict:
        rt = {
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Dnt": "1",
            "Origin": "https://www.ordz.games",
            "Referer": "https://www.ordz.games/",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": self.agent_x,
        }
        return rt

    def _header_in_game(self):
        rt = {
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Dnt": "1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip,deflate,br",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://fightclub.ordz.games",
            "Referer": "https://fightclub.ordz.games/",
            "User-Agent": self.agent_x,
        }
        return rt

    def header_doc_ref(self, ref: str) -> dict:
        f = self.gen_header()
        f.update(
            {
                "Content-Type": "application/json",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Referer": ref,
            }
        )
        return f

    def header_api_ref(self, content: str) -> dict:
        f = self.gen_header()
        f.update({"Referer": content})
        return f

    def api_action_ref(self, path: str, rq: dict, ref: str):
        return self.api_action_h(path, rq, self.header_api_ref(ref))

    def api_read_public(self, path: str, header_x: dict, q: dict = None):
        """print(path)
        print(header_x)
        print(q)"""
        if path.startswith("https://"):
            resp = self.session.get(path, params=q, headers=header_x)
        else:
            resp = self.session.get(f"{HOST_API}/{path}", params=q, headers=header_x)
        if resp.status_code == 500:
            time.sleep(4)
            return self.api_read_public(path, header_x, q)
        # print(path)
        if resp.status_code != 200:
            print(
                "not working on check token =========================> ",
                resp.status_code,
            )
            print(resp.text)
            raise RequestErro()
        try:
            resp_p = json.loads(resp.content)
            return self.res_process_handle(resp_p)
        except json.JSONDecodeError as e:
            print("NO JSON FOUND.", e)
            print(resp.text)
            exit(0)

    def api_action_h(self, path: str, rq_data: dict, header_x: dict, handler=None):
        resp = self.session.post(path, json=rq_data, headers=header_x)

        if resp.status_code == 500:
            time.sleep(4)
            return self.api_action_h(path, rq_data, header_x)

        if resp.status_code != 200:
            print("@ bad response ===> ", resp.status_code)
            print(resp.content)
            raise RequestErro()

        print(path)
        time.sleep(0.5)
        try:
            json_response = json.loads(resp.content)
            if handler is None:
                return self.res_process_handle(json_response)
            else:
                return handler(json_response)
        except json.JSONDecodeError as e:
            print("NO JSON FOUND.", e)
            print(resp.text)
            exit(0)

    def api_action(self, path: str, rq: Optional[dict] = None):
        return self.api_action_h(path, rq, self.hloginsession())

    def api_read(self, path: str, r: dict = None):
        res = self.api_read_public(path, self.hloginsession(), r)
        time.sleep(2)
        return self.res_process_handle(res)

    def res_boolean_handle(self, res) -> bool:
        print(res)
        if isinstance(res, dict):
            if "code" in res:
                response_code = res["code"]
                if response_code == 1000:
                    return True
                else:
                    self.res_process_handle(res)
                    return False
        return False

    def res_process_handle(self, res):
        if isinstance(res, dict):
            message = res["message"] if "message" in res else ""
            if "code" in res:
                response_code = res["code"]
                if response_code == 1000:
                    # OK
                    ...
                elif response_code == 2000:
                    print("You have got a special message.")
                    print(res)
                    if message == "unknown error":
                        raise UnknownErr()
                    raise UnboundTwitterErr()

                elif response_code == 20219:
                    print("================")
                    print("TOKEN is IN USE")
                    print("================")

                elif response_code == 200113:

                    if message == "No sign.":
                        raise NoSignature()

                elif response_code == 20557:
                    print(message)
                    raise FreePlayLimited()

                elif response_code == 20247:
                    raise UnboundTwitterErr()

                elif response_code == 20230:

                    print(message)
                    raise InvalidToken()

                elif response_code == 200106:
                    print(message)
                    raise InvalidToken()

                elif response_code == 200111:
                    print(message)
                    raise TwitterAccountHasBeenBound()
                elif response_code == 201001:
                    raise Rekt()
                elif response_code == 3000:
                    print("error-3000")
                    print(message)
                elif response_code == 200110:
                    print(message)
                    raise AccountHasBeenBoundWithTwitter()
                else:
                    print(f"unknown error {response_code} > message")
                    print(message)

            if "data" not in res:
                print(message)

                raise RequestErro()

            return res
        else:
            return res
