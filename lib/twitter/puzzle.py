import base64
import json
import os.path
import re
from pynpm import NPMPackage
import urllib.parse

DOM_BASE = "./dom_test"
DATAPATH_BASE = "./cache"
"""
try:
    import wurlitzer
except:
    os.system('python -m pip install wurlitzer')
    import wurlitzer

"""


class NodeVersionOut(Exception):
    pass


def solve_ui_metric(session_client, h: dict, auth: dict, cburl: str):
    img_data = json.dumps({
        "username_or_email": auth["user"],
        "redirect_after_login": cburl
    }).encode()
    code = base64.b64encode(img_data)
    referral_content = urllib.parse.quote(json.dumps({
        "requested_variant": str(code)
    }).encode())
    pref = f"https://twitter.com/i/flow/login?input_flow_data={referral_content}"
    h.update({
        "Referer": pref
    })
    print("request before ui metrics")
    print(h)
    r = session_client.get("https://twitter.com/i/js_inst?c_name=ui_metrics", headers=h)
    if r.status_code != 200:
        print("err from ui metrics", r.status_code)
        return False

    js_content = r.text
    y = js_content.strip().split("\n")
    last_line = y[len(y) - 1].strip()
    last_line = f"const verificationUI={last_line.replace('();', '')};"
    one_last_line = f"export default verificationUI;"
    dos = y[:len(y) - 1]
    first_line = dos[0].replace("()", "(window,document,result)")
    key_value = dos[3].replace("var ", "").replace(";", "").strip()
    callback_line = f"result({key_value});"
    dos.append(last_line)
    dos.append(one_last_line)
    dos = [first_line] + dos[1:9] + [callback_line] + dos[12:]
    new_doc = "\n".join(dos)
    save_puzzle_file(new_doc)
    return solve_puzzle_js_file("twitter")


def save_puzzle_file(content: str) -> str:
    file_path = os.path.join(DOM_BASE, "ui_metric.js")
    with open(file_path, "wb") as f:
        f.write(bytearray(content, "utf-8"))
        f.close()
    return file_path


def solve_puzzle_js_file(script_name: str) -> str:
    file_path = os.path.join(DOM_BASE, "package.json")
    node_modules = os.path.join(DOM_BASE, "node_modules")
    twitter_res = os.path.join(DOM_BASE, "twitter_res.txt")
    node_version = os.path.join(DOM_BASE, "node_version.txt")
    _package = NPMPackage(file_path, shell=False)
    if os.path.exists(node_modules) is False:
        _package.install(wait=True)
    _package.run_script("checker")
    if "v21" not in read_console(node_version):
        raise NodeVersionOut()
    _package.run_script(script_name, '--silent')
    content = read_console(twitter_res)
    return content.strip()


def read_cookie(header: dict) -> dict:
    path = os.path.join(DATAPATH_BASE, "x_cookie")
    content_cookie = read_console(path)
    if content_cookie != "":
        header.update({
            "Cookie": content_cookie
        })
    return header


def save_cookie(session_client):
    b = []
    b.append("remember_checked_on=1")
    b.append("night_mode=1")
    b.append("des_opt_in=Y")
    for c in session_client.cookies:
        text_content = f"{c.name}={c.value}"
        b.append(text_content)
    with open(os.path.join(DATAPATH_BASE, "x_cookie"), "wb") as f:
        f.write(bytearray(";".join(b), "utf-8"))
        f.close()


def read_console(path) -> str:
    content = ""
    if os.path.exists(path) is False:
        return content
    with open(path, "r") as d:
        content = d.read()
        d.close()
    return content


def read_file_lines(filename: str) -> list:
    content_line = []
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            content_line.append(content.strip().replace("\n", ""))
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


def get_param_from_url(url, param_name):
    return [i.split("=")[-1] for i in url.split("?", 1)[-1].split("&") if i.startswith(param_name + "=")][0]

def read_file_total_lines(filename: str) -> int:
    print(f"count lines from {filename}")
    with open(filename, 'r') as fp:
        for count, line in enumerate(fp):
            pass
        fp.close()
    print('Total Lines', count + 1)
    return count + 1
