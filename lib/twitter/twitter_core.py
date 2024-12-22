import os.path
import re
import time
import urllib.parse
import pyotp
import requests
from .decode import DecodeHTML
from .puzzle import solve_ui_metric, save_cookie, read_cookie, read_file_lines, read_file_at_line, \
    read_file_total_lines, read_console, get_param_from_url
from lib.cookie3 import generateCookieFromUsual

DATAPATH_BASE = "./cache"
CONSUMMER_KEY = "uWlhrNXBlyNsYY0ulXvbAqSlq"
CONSUMMER_API = "KgKY0IENQPSXNmhsirSQeUUuvmPzrb4qiLtyvn0FeDaC7WhcpN"
ACCESS_KEY = "68903197-ZaPwVVRefNExQEXw2yIUkpq1ATyw1GooW1F2jrrgg"
ACCESS_TOKEN = "zo0EEPNAHLHys0Cn66FwalhSlIyFq1crdhug9cffj9r74"
BEARER = "AAAAAAAAAAAAAAAAAAAAAB6%2BsAEAAAAAgCYbTUfM3pN2OUgyHRHUnw%2FYGuo%3DheHOM3kTkMOuvRvnI2FoKNXWOh90ha4DDBp1BQGLrsmAnUXonT"

try:
    import tls_client
except:
    os.system('python -m pip install tls-client')
    import tls_client


class ShowF2AErr(Exception):
    pass


class TwitterErrorFailure(Exception):
    pass


class MissingKeyInfo(TwitterErrorFailure):
    pass


class TwitterAuthTokenNotFound(MissingKeyInfo):
    pass


class TwitterUserNotFound(MissingKeyInfo):
    pass


class TwitterPasswordNotFound(MissingKeyInfo):
    pass


class TwitterExpired(TwitterErrorFailure):
    pass


class TwitterAccountLocked(TwitterErrorFailure):
    pass


class TwitterFileDecodeErr(TwitterErrorFailure):
    pass


class X:
    auth_file_name: str
    account_limit: int

    def __init__(self):
        self.session = tls_client.Session(
            client_identifier="Firefox110",
            supported_signature_algorithms=[
                "ECDSAWithSHA256",
                "SHA256",
                "SHA384",
                "SHA512",
                "SHA256WithRSAEncryption",
                "SHA384WithRSAEncryption",
                "SHA512WithRSAEncryption",
                "ECDSAWithSHA384"
            ],
            supported_versions=["GREASE", "1.3", "1.2"],
            key_share_curves=["GREASE", "X25519"],
            cert_compression_algo="brotli",
            pseudo_header_order=[
                ":method",
                ":authority",
                ":scheme",
                ":path"
            ],
            connection_flow=15663105,
            header_order=[
                "accept",
                "user-agent",
                "accept-encoding",
                "accept-language"
            ]
        )
        self.agent = ""
        self.auth_file_name = ""
        self.port_vpn = 7890
        self._user_index = 0

    def init_load_file(self, account_file: str):
        path = os.path.join(DATAPATH_BASE, account_file)
        self.auth_file_name = path
        self.account_limit = read_file_total_lines(path)

    @property
    def port_vpn(self) -> int:
        """I'm the 'x' property."""
        return self._port_vpn

    @port_vpn.setter
    def port_vpn(self, value: int):
        self._port_vpn = value
        if value > 0:
            self.session.proxies = {
                'http': f'http://127.0.0.1:{value}',
                'https': f'http://127.0.0.1:{value}'
            }
        else:
            self.session.proxies = None

    def header_file(self) -> dict:
        hh = {
            "Accept": "*/*",
            "Referer": "https://api.twitter.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "Dnt": "1",
            "User-Agent": self.agent
        }
        return hh

    def header_base(self) -> dict:
        hh = {
            "MI": "P",
            "Perf": "7469935968",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "text/html;charset=utf-8",
            "Content-Security-Policy": "default-src 'none'; connect-src 'self'; font-src https://abs.twimg.com https://abs-0.twimg.com data:; frame-src 'self' twitter:; frame-ancestors 'self' https://tweetdeck.twitter.com https://tdapi-staging.smf1.twitter.com https://tdapi-staging.atla.twitter.com https://tdapi-staging.pdxa.twitter.com https://tweetdeck.localhost.twitter.com; img-src https://abs.twimg.com https://*.twimg.com https://pbs.twimg.com data:; media-src 'none'; object-src 'none'; script-src https://abs.twimg.com https://abs-0.twimg.com https://twitter.com https://mobile.twitter.com; style-src https://abs.twimg.com https://abs-0.twimg.com; report-uri https://twitter.com/i/csp_report?a=NVQWGYLXFVWG6Z3JNY%3D%3D%3D%3D%3D%3D&ro=false;",
            "Referer": "https://api.twitter.com/"
        }

        hh.update({
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site"
        })

        return read_cookie(hh)

    def headerP1(self) -> dict:
        passwordheader = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Dnt": "1",
            "Origin": "https://api.twitter.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.agent
        }
        return passwordheader

    def headerP2(self) -> dict:
        passwordheader = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Dnt": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.agent
        }
        return passwordheader

    def use_next_x_account(self) -> dict:
        self._user_index = self._user_index + 1
        return self.read_user_at(self._user_index)

    def twoFactorNet(self, code: str) -> str:
        content = ""
        with requests.post("http://2fa.show/", data={"2fa": code}, headers={
            "Host": "2fa.show",
            "Origin": "http://2fa.show",
            "Referer": "http://2fa.show/",
        }) as r:
            rex = r"<font color=\"#FF0000\">(\d+)"
            line = r.text
            matches = re.finditer(rex, line)
            for matchNum, match in enumerate(matches, start=1):
                content = match.group(1)
                if len(content) > 0:
                    break
            if content == "":
                raise ShowF2AErr()
        return content

    def twoFactorFast(self, code: str) -> str:
        totp = pyotp.TOTP(code)
        return totp.now()

    def read_cookie(self) -> str:
        path = os.path.join(DATAPATH_BASE, "x_cookie")
        if os.path.exists(path) is True:
            with open(path, 'r') as f:
                # Press the green button in the gutter to run the script.
                k = f.read()
                return k
        else:
            return ""

    def read_user_at(self, index: int) -> dict:
        n = index % self.account_limit
        line = read_file_at_line(self.auth_file_name, n)
        print(line)
        if "----" in line:
            line = line.split("----")
        elif "————" in line:
            line = line.split("————")
        elif "--" in line:
            line = line.split("--")
        elif "——" in line:
            line = line.split("——")

        if isinstance(line, str):
            raise TwitterFileDecodeErr()

        self._user_index = n
        tmp = {
            "user": line[0],
            "pw": line[1],
            "email": line[2],
            "token": line[3],
            "code_f2a": line[4] if len(line) >= 5 else "",
        }
        print(tmp)
        return tmp

    def test_ui_metric(self):
        user = self.read_user_at(0)
        url_cb = "xxxxx"
        rf = solve_ui_metric(self.session, self.header_file(), user, url_cb)
        print("========= RF")
        print(rf)
        print("========= ENDER")

    def bindTwitterWithAuthToken(self, user: dict, hot_token: str, cb: str, header_from_ordz: dict):
        if "token" not in user \
                or user["token"] is None \
                or len(user["token"]) > 40 \
                or len(user["token"]) < 40:
            raise TwitterAuthTokenNotFound()

        header_from_ordz.update({
            "Cookie": generateCookieFromUsual({
                "auth_token": user["token"],
                "night_mode": 1,
                "remember_checked_on": 1,
            })
        })

        r = self.session.get("https://api.twitter.com/oauth/authenticate", params={
            "oauth_token": hot_token,
            "oauth_callback": cb
        }, headers=header_from_ordz, allow_redirects=True)

        save_cookie(self.session)
        html_content = r.text
        # print(html_content)
        # Create a BeautifulSoup object to parse the HTML content
        soup = DecodeHTML.toCache(html_content)
        if r.status_code != 200:
            print("Whoops!", r.status_code)
            print(soup.text())
            if "this account is temporarily locked" in soup.text():
                raise TwitterAccountLocked()
            if "There is no request token for this page" in soup.text():
                raise TwitterAccountLocked()
            time.sleep(100)
            return False

        # Create a BeautifulSoup object to parse the HTML content

        if soup.found("Redirecting you back to the application. This may take a few moments.") is False:
            # Find the input element with name="authenticity_token"
            authenticity_token = soup.get_input_attribute_val('authenticity_token')
            redirect_after_login = soup.get_input_attribute_val('redirect_after_login')
            oauth_token = soup.get_input_attribute_val('oauth_token')
            r = self.session.post("https://api.twitter.com/oauth/authenticate", params={
                "authenticity_token": authenticity_token,
                "redirect_after_login": redirect_after_login,
                "oauth_token": oauth_token,
            }, headers=header_from_ordz, allow_redirects=True)
            if r.status_code == 403:
                print("token is invalid or expired.")
                return False
            if r.status_code == 200:
                print("big success")
            soup = DecodeHTML.toCache(r.text)

        redirection = soup.get_twitter_callback_x()
        if redirection == "" or None:
            print(redirection)
            raise TwitterErrorFailure()
        oauth_token = get_param_from_url(redirection, "oauth_token")
        oauth_verifier = get_param_from_url(redirection, "oauth_verifier")
        return (oauth_token, oauth_verifier)

    def binding_action_callback(self, redirection: str, header_ordz):
        # this is the general suggested by the twitter official page
        r = self.session.get(redirection, headers=header_ordz, allow_redirects=True)
        if r.status_code == 200:
            print("redirecting success bind account.")

    def bindTwitterAccount(self, user: dict, hot_token: str, cb: str, header_from_ordz: dict):

        if "pw" not in user or user["pw"] is None:
            raise TwitterPasswordNotFound()

        if "user" not in user or user["user"] is None:
            raise TwitterUserNotFound()

        # login and twitter starting from here.
        r = self.session.get("https://api.twitter.com/oauth/authenticate", params={
            "oauth_token": hot_token,
            "oauth_callback": cb
        }, headers=header_from_ordz, allow_redirects=True)

        save_cookie(self.session)
        html_content = r.text
        # print(html_content)
        # Create a BeautifulSoup object to parse the HTML content
        soup = DecodeHTML.toCache(html_content)

        if r.status_code != 200:
            print("something error", r.status_code)
            print(soup.text())
            if "this account is temporarily locked" in soup.text():
                raise TwitterAccountLocked()

            time.sleep(100)
            return False

        # Find the input element with name="authenticity_token"
        authenticity_token_input = soup.get_input_attribute_val('authenticity_token')
        url_cb = soup.get_input_attribute_val('redirect_after_login')
        # now login the first page
        # now login
        rf_content = solve_ui_metric(self.session, self.header_file(), user, url_cb)
        if len(rf_content) == 0:
            raise TwitterErrorFailure()

        data_1 = self.login_twitter_page_1(
            start_req={
                "authenticity_token": authenticity_token_input,
                "redirect_after_login": url_cb,
                "force_login": False,
                "oauth_token": hot_token,
                "session[username_or_email]": user["user"],
                "session[password]": user["pw"],
                "ui_metrics": rf_content
            }
        )

        if data_1 is False:
            raise TwitterErrorFailure()

        data_2 = self.login_twitter_page_2(web_data=data_1, userInfo=user)

        return self.login_twitter_page_3(web_data=data_2)

    def login_twitter_page_1(self, start_req: dict):
        page1 = self.headerP1()
        page1 = read_cookie(page1)
        _callback = "https://www.ordz.games"
        _callback = urllib.parse.quote(_callback.encode())
        auth_url = f"https://api.twitter.com/oauth/authenticate?oauth_token={start_req['oauth_token']}&oauth_callback={_callback}"
        page1.update({
            "Referer": auth_url
        })
        r = self.session.post(
            "https://api.twitter.com/oauth/authenticate",
            data=start_req, headers=page1, allow_redirects=True
        )
        html_content = self.twitterErroControl(r, 1)
        if html_content is False:
            return False

        soup = DecodeHTML(html_content)
        # Find the input element with name="authenticity_token"
        url_cb = soup.get_input_attribute_val('redirect_after_login')
        user_id = soup.get_input_attribute_val('user_id')
        challenge_id = soup.get_input_attribute_val('challenge_id')
        challenge_type = soup.get_input_attribute_val('challenge_type')
        platform = soup.get_input_attribute_val('platform')

        return {
            "platform": platform,
            "user_id": user_id,
            "challenge_type": challenge_type,
            "challenge_id": challenge_id,
            "redirect_after_login_verification": url_cb,
        }

    def twitterErroControl(self, r, stage: int = 0):
        html_content = r.text
        if r.status_code != 200:
            print("Still not OKAY..", r.status_code, stage)

            if "expired because it is too old" in html_content:
                raise TwitterExpired()

            if "This account is suspended." in html_content:
                raise TwitterAccountLocked()

            if "lock" in r.url:
                print(f"Oops this account is locked. {self._user_index}")
                raise TwitterAccountLocked()

            if "That's the special key we need from applications asking to use your Twitter account." in html_content:
                print("request puzzle not successfully solved.")
                return False

            print(f"stage at {stage}")
            print(html_content)

            return False
        return html_content

    def login_twitter_page_2(self, web_data: dict, userInfo: dict) -> dict:
        page2hd = self.headerP2()
        page2hd = read_cookie(page2hd)

        r = self.session.get(
            "https://twitter.com/account/login_verification", params=web_data,
            headers=page2hd, allow_redirects=True)

        html_content = self.twitterErroControl(r, 2)
        if html_content is False:
            return False

        html_content = r.text
        soup = DecodeHTML(html_content)
        # Find the input element with name="authenticity_token"
        url_cb = soup.get_input_attribute_val('redirect_after_login')
        user_id = soup.get_input_attribute_val('user_id')
        challenge_id = soup.get_input_attribute_val('challenge_id')
        challenge_type = soup.get_input_attribute_val('challenge_type')
        platform = soup.get_input_attribute_val('platform')

        print("OK. login_twitter_page_2")

        data_pack = {
            "authenticity_token": url_cb,
            "challenge_id": challenge_id,
            "user_id": user_id,
            "challenge_type": challenge_type,
            "platform": platform,
            "redirect_after_login": url_cb,
            "remember_me": False,
            "challenge_response": self.twoFactorFast(userInfo["code_f2a"])
        }

        print(data_pack)
        print(userInfo)
        print(page2hd)
        print("END DATA =============== login_twitter_page_2")
        return data_pack

    def login_twitter_page_3(self, web_data: dict):
        page3hd = self.headerP2()
        page3hd = read_cookie(page3hd)
        r = self.session.get(
            "https://twitter.com/account/login_verification", params=web_data,
            headers=page3hd, allow_redirects=True)
        html_content = self.twitterErroControl(r, 3)
        if html_content is False:
            return False
        print(html_content)


class XTwitter(X):
    def __init__(self):
        super().__init__()
