# !/usr/bin/env python
# coding: utf-8
import re

from subprocess import Popen, PIPE
import json
import os.path
from typing import Union

from bs4 import BeautifulSoup
from lib.const import DATAPATH_BASE


class IOBase:
    def _loadjson(self, path):
        with open(path, 'r') as fp:
            data = json.load(fp)
            fp.close()
        return data

    def _extraction(self, head_line_json: str, bug: bool = False, showinJson: bool = True):
        payload_x = ""
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        with open(path, 'r') as fp:
            # read all lines using readline()
            dumps = fp.readlines()
            for line in dumps:
                if head_line_json in line:
                    line = line.strip()
                    prematerial = line.replace(head_line_json, "").strip()
                    if showinJson is False:
                        payload_x = prematerial[:-1] if bug is False else prematerial
                    else:
                        if bug is True:
                            payload_x = json.loads(prematerial)
                        else:
                            payload_x = json.loads(prematerial[:-1])

            fp.close()

        return payload_x

    def _find_text(self, search_keyword: str):
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        with open(path, 'r') as g:
            duline = g.readlines()
            for line in duline:
                if search_keyword in line:
                    return True
            g.close()

        return False

    def _extract_from_block(self, head_line_json: str, endline_str: str, isJson: bool = True) -> Union[dict, str, int]:
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        payload_x = {}
        with open(path, 'r') as fp:
            # read all lines using readline()
            dumps = fp.readlines()
            for line in dumps:
                if head_line_json in line:
                    starting_index = line.find(head_line_json) + len(head_line_json)
                    ending_index = line.find(endline_str) - 1
                    payload_x = line[starting_index:ending_index]
            fp.close()

        if isJson is True:
            payload_x = json.loads(payload_x)

        return payload_x

    def _extract_html_div_content(self, tag_id: str) -> str:
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        html_content = ""
        with open(path, 'r') as fp:
            html_content = fp.read()
            fp.close()
        if html_content == "":
            return False
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find('div', {'id': tag_id}).text
        content = content.strip()
        return content

    def _extract_by_regx(self, regex) -> list:
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        payload_x = []
        with open(path, 'r') as fp:
            dat = fp.read()
            matches = re.finditer(regex, dat, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                the_number = match.group(1)
                # print(the_number)
                payload_x.append(the_number)

            fp.close()
        return payload_x

    def _capture_js_block(self, start_cap_line: str, end_cap_line: str, offset_back_line: int = 1,
                          additional_line_js: str = "") -> dict:
        path = os.path.join(DATAPATH_BASE, "tmp.txt")

        blocktx = []
        nb = 0
        start = 0
        end = 0

        with open(path, 'r') as fp:
            # read all lines using readline()
            dumps = fp.readlines()
            for line in dumps:
                if start_cap_line in line:
                    start = nb
                if end_cap_line in line:
                    end = nb

                if start > 0 and end == 0:
                    blocktx.append(line)

                if end > 0:
                    break
                nb += 1
            fp.close()

        path_tmp = os.path.join(DATAPATH_BASE, "tmp.js")
        blocktx = blocktx[:len(blocktx) - offset_back_line]
        blocktx.append(additional_line_js)
        my_str_as_bytes = str.encode("".join(blocktx))
        self._save_bytes(my_str_as_bytes, path_tmp)
        return self.evaluate_javascript(path_tmp)

    def _save_tmp(self, content):
        """
        save the content bytes into tmp file
        :param content:
        :return:
        """
        path = os.path.join(DATAPATH_BASE, "tmp.txt")
        self._save_bytes(content, path)

    def evaluate_javascript(self, path: str):
        """Evaluate and stringify a javascript expression in node.js, and convert the
        resulting JSON to a Python object"""
        node = Popen(['node', path], stdin=PIPE, stdout=PIPE)
        # stdout, _ = node.communicate(f'console.log(JSON.stringify({s}))'.encode('utf8'))
        stdout, _ = node.communicate()
        filter1 = stdout.decode('utf8')
        filter1 = filter1.replace("\n", "")
        # filter1 = filter1.replace("None", "")
        # filter1 = filter1.replace("[Array]", "[]")
        # filter1 = filter1.replace("[Object]", "{}")
        # return fd
        # my_str_as_bytes = str.encode(filter1)
        # self._save_bytes(my_str_as_bytes, path)
        return json.loads(filter1)

    def _save_bytes(self, content, file_name):
        """
        save the bytes info into the file
        :param content:
        :param file_name:
        :return:
        """
        file_object = None
        try:
            file_object = open(file_name, 'wb')
            file_object.truncate(0)
        except FileNotFoundError:
            file_object = open(file_name, 'a+')
        finally:
            # file_object.buffer.write(content)
            file_object.write(content)
            file_object.close()
