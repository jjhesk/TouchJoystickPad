import os.path

DATAPATH_BASE = "./cache"
ERROR_COOKIE = "Pls update cookie file"
COOKIE_FILE = "tmp_cookie"

import tls_client


def readCookieFromFile() -> str:
    path = os.path.join(DATAPATH_BASE, COOKIE_FILE)
    return read_console(path)


def read_cookie_into_header(header: dict, specific_file: str = COOKIE_FILE) -> dict:
    path = os.path.join(DATAPATH_BASE, specific_file)
    content_cookie = read_console(path)
    if content_cookie != "":
        header.update({
            "Cookie": content_cookie
        })
    return header


def read_console(path) -> str:
    content = ""
    if os.path.exists(path) is False:
        print(f"File {path} not exist. return empty.")
        return content
    with open(path, "r") as d:
        content = d.read()
        d.close()
    return content


def generateCookieFromUsual(map: dict):
    map.update({
        "lang": "en",
    })
    return makeCookie(map)


def makeCookie(given_map: dict) -> str:
    b = []
    for g in given_map:
        b.append(f"{g}={given_map[g]}")
    return ";".join(b)


class CookieExt:
    def __init__(self):
        self.cookie = ""
        self.sqldb = None

    def bindsql(self, sql_db_module):
        self.sqldb = sql_db_module

    def update_cookie(self, session: tls_client.Session):
        if self.sqldb == None:
            return
        uuid = self.sqldb.get_raw_uuid(self.sqldb.tble_member, self.sqldb.user_id)
        b = {
            "ref_id": "1962391",
            "tc1": "w4mdq31aliag72gp2ssjfq9c",
            "tc2": "Adsterra-David",
            "tc3": "FR",
            "tc5": "19615710",
            "source": "96bfc843-3d0a-43e6-983d-914746b3a7f8",
            "campaign": "799291",
            "age_verification": "1",
            "_pk_id.2.6e07": "b0b6057083e5319b.1699031411.",
            "_pk_ses.2.6e07": "1",
            "member_guid": uuid,
            "player_id": self.sqldb.user_id,
        }
        for c in session.cookies:
            if c.name == "session_token":
                continue
            b.update({
                c.name: c.value
            })

        self.sqldb.update_cookie(generateCookieFromUsual(b))

    def patch_cookie(self, session: tls_client.Session):
        if self.sqldb == None:
            return
        cookie = self.db_get_cookie()
        for c in session.cookies:
            if c.name == "session_token":
                continue
            if c.name == "HAPBK":
                cookie.update({
                    "HAPBK": c.value
                })
            if c.name == "HH_SESS_13":
                cookie.update({
                    "HH_SESS_13": c.value
                })
            if c.name == "player_id":
                cookie.update({
                    "player_id": c.value
                })
        b = []
        for g in cookie:
            b.append(f"{g}={cookie[g]}")
        self.sqldb.update_cookie(";".join(b))

    def read_cookie(self) -> str:
        if self.sqldb == None:
            return ""
        return self.sqldb.getAuthCookie()

    def db_get_cookie(self) -> dict:
        t = self.read_cookie()
        cookie = {}
        r = t.split(";")
        for n in r:
            f = n.split("=")
            if len(f) == 2:
                cookie[f[0]] = f[1]
                cookie.update()
        return cookie
