# !/usr/bin/env python
# coding: utf-8
import codecs
import datetime
import io
import logging
import os
import re
import json
import time
from os.path import isdir
import random
from os.path import join as pjoin, dirname, realpath
from typing import TextIO

from lib.const import LocalConf

from Crypto.Cipher import AES
from base64 import b64encode, b64decode


class RandomAgentClass:
    @staticmethod
    def randomagent():
        f = pjoin(dirname(realpath(__file__)), "../dat/wins.txt")
        with open(f) as ua_file:
            lines = ua_file.readlines()
            user_agency = random.choice(lines).strip()
        print("device applied")
        print(user_agency)
        return user_agency

    @staticmethod
    def first():
        f = pjoin(dirname(realpath(__file__)), "../dat/wins.txt")
        with open(f) as ua_file:
            lines = ua_file.readlines()
            user_agency = lines[0].strip()
        print("device applied")
        print(user_agency)
        return user_agency


class PromptUtil:
    @staticmethod
    def random_image():
        f = os.path.join(LocalConf.CACHE_PATH, "prompt_girls.txt")
        with open(f) as ua_file:
            lines = ua_file.readlines()
            prompt = random.choice(lines).strip()
            ua_file.close()
        return prompt

    @staticmethod
    def rand_chat():
        f = os.path.join(LocalConf.CACHE_PATH, "chat_prompts.txt")
        with open(f) as ua_file:
            lines = ua_file.readlines()
            prompt = random.choice(lines).strip()
            ua_file.close()
        return prompt


class NameUtil:

    @staticmethod
    def withFix(pre: str, sub: str, number: bool):
        A = random.choice(LocalConf.FIRST_NAME_DICT).strip()
        A = A.replace("\n", "")
        B = random.choice(LocalConf.SURNAME_DICT).strip()
        B = B.replace("\n", "")
        K = random.randrange(111, 999, 1)
        return pre + A + B + K if number is True else "" + sub

    @staticmethod
    def init_dict():
        f1 = os.path.join(LocalConf.ASSETS_DIR, "kr_surname.txt")
        f2 = os.path.join(LocalConf.ASSETS_DIR, "firstname.txt")
        with open(f1) as ua_file:
            LocalConf.SURNAME_DICT = ua_file.readlines()
            ua_file.close()

        with open(f2) as ua_file:
            LocalConf.FIRST_NAME_DICT = ua_file.readlines()
            ua_file.close()

    @classmethod
    def get_name(cls, withNumber: bool = False):
        return cls.withFix("", "", withNumber)

    @classmethod
    def get_solname(cls, withNumber: bool = False):
        return cls.withFix("", ".sol", withNumber)

    @classmethod
    def get_ethname(cls, withNumber: bool = False):
        return cls.withFix("", ".eth", withNumber)

    @classmethod
    def get_name_simple(cls):
        return cls.withFix("", "", False)


class BufferKeyFile:
    _file: str
    _hot_content: TextIO
    _tmp_io_array: list

    def __init__(self):
        self._file = "tmp_remote_execution.sh"
        self._hot_content = None
        self._tmp_io_array = []

    def defaultName(self):
        self._file = "tmp_remote_execution.sh"
        self._check_file()

    def setName(self, file_name: str):
        self._file = file_name
        self._check_file()
        return self

    @property
    def path(self):
        return os.path.join(LocalConf.CACHE_PATH, self._file)

    @property
    def execution_cmd(self) -> str:
        return self._file
        #  return f"sh {self._file}"

    def _check_file(self):
        with open(self.path, "w") as f_io:
            f_io.write("")
            f_io.close()

    def open_file_io_buffer(self, method: str = "ab"):
        return open(self.path, method)

    def new_bash(self):
        self.clear()
        self.add_cmd("#!/bin/bash")
        # self.add_cmd("source ~/.profile")

    def new_keyfile(self, name: str):
        self._file = name
        self._tmp_io_array = []
        self._check_file()

    def clear(self):
        self._check_file()

    def write_content(self, block: str):
        with open(self.path, "w") as f_io:
            f_io.write(block)
            f_io.close()

    def write_content_b(self, block: bytes):
        with open(self.path, "wb") as f_io:
            f_io.write(block)
            f_io.close()

    def add_cmd(self, line: str, at_line: int = -1):
        line = line + "\n"
        with open(self.path, "a") as f_io:
            if at_line == -1:
                f_io.write(line)
            else:
                f_io.seek(at_line, os.SEEK_END)
                f_io.write(line)
            f_io.close()

    def add_reminder(self, r: str):
        if r not in self._tmp_io_array:
            self._tmp_io_array.append(r)

    def reminder_consolidate(self):
        with open(self.path, "w") as f_io:
            f_io.write("\n".join(self._tmp_io_array))
            f_io.close()

    def get_in_array(self) -> int:
        return len(self._tmp_io_array)

    def this_file_filter(self, items: list):
        text_pl = ""
        with open(self.path, "r") as f_io:
            text_pl = f_io.read()
            f_io.close()
        for symbol in items:
            text_pl = text_pl.replace(symbol, "")
        self.write_content(text_pl)

    def remove_color(self):
        with open(self.path, "r") as f_io:
            text_pl = f_io.read()
            f_io.close()
            regex = re.compile(r"\[38;2(;\d{,3}){3}m")
            text_pl = regex.sub("", text_pl)
            self.write_content(text_pl)

    def save_as(self, file_name: str):
        base_database = os.path.join(LocalConf.CACHE_PATH, file_name)
        content = ""
        with open(self.path, "r") as f_io:
            content = f_io.read()
            f_io.close()

        with open(base_database, "w+") as f_io:
            f_io.write(content)
            f_io.close()

        print("save as done.")

    def read_from(self, file_name: str):
        io_source = os.path.join(LocalConf.CACHE_PATH, file_name)
        self._hot_content = open(io_source, "r")

    def open_io_src_a(self, file_name: str) -> TextIO:
        path_file = os.path.join(LocalConf.CACHE_PATH, file_name)
        return self._open_io_src(path_file, "a")

    def _open_io_src(self, full_path: str, method: str):
        x = open(full_path, "w")
        x.truncate(0)
        x.close()
        return open(full_path, method)

    def save_as_split_files(self, lines_group: int, file_format: str, encrypted: bool = False):
        """
        the split file function automatically.
        :param lines_group: the maximum lines in one text file
        :param file_format: the file name in the given format
        :return:
        """
        if self._hot_content is None:
            print("hot content is not defined. use read_from to read the file content")
            return
        if "{COUNT_INDEX}" not in file_format:
            print("format keyword {COUNT_INDEX} is not found in the line.")
            return
        loops = 1
        limit_line = lines_group
        end_count = 0
        hot_content_io = self.open_io_src_a(file_format.format(COUNT_INDEX=loops))
        file_closed = False
        for x, line in enumerate(self._hot_content):
            end_count = x
            pass
        self._hot_content.seek(io.SEEK_SET)
        for count, line in enumerate(self._hot_content):
            if count > limit_line - 2:
                hot_content_io.write(line.rstrip("\n"))
                hot_content_io.close()
                file_closed = True

                if count < end_count:
                    loops += 1
                    limit_line = loops * lines_group
                    hot_content_io = self.open_io_src_a(file_format.format(COUNT_INDEX=loops))
                    file_closed = False

            else:
                hot_content_io.write(line)

        # end of the file
        if file_closed is False:
            hot_content_io.close()

        print(f"All files are split into {loops} groups and now done!")
        if encrypted is True:
            print("now trying to encrypt the files")
            n = 0
            while n < loops:
                file = file_format.format(COUNT_INDEX=(n + 1))
                test_crpt = Crypt()
                self.read_from(file)
                content = self._hot_content.read()
                self._hot_content.close()
                enc_content = test_crpt.encrypt(content, LocalConf.DATA_SALT)
                #
                iop = self.open_io_src_a(file)
                iop.write(enc_content)
                iop.close()

                self.read_from(file)
                test_enc_text = self._hot_content.read()
                test_line = test_crpt.decrypt(test_enc_text, LocalConf.DATA_SALT)
                test_line = test_line.split("\n")
                for e in test_line:
                    words = e.split(" ")
                    word_count = len(words)
                    assert word_count == 12
                print("test result OK!", file)
                n += 1


class Crypt:

    def __init__(self, salt='JH9wNrzmmCfn8OI2'):
        self.salt = salt.encode('utf8')
        self.enc_dec_method = 'utf-8'

    def encrypt(self, str_to_enc, str_key):
        try:
            aes_obj = AES.new(str_key.encode('utf-8'), AES.MODE_CFB, self.salt)
            hx_enc = aes_obj.encrypt(str_to_enc.encode('utf8'))
            mret = b64encode(hx_enc).decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Encryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Encryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)

    def decrypt(self, enc_str, str_key):
        try:
            aes_obj = AES.new(str_key.encode('utf8'), AES.MODE_CFB, self.salt)
            str_tmp = b64decode(enc_str.encode(self.enc_dec_method))
            str_dec = aes_obj.decrypt(str_tmp)
            mret = str_dec.decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Decryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Decryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)


def combine_keys(folder_in_cache: str):
    combined_file = "bank_capital.txt"
    sxx = []
    path_run = os.path.join(LocalConf.CACHE_PATH, folder_in_cache)
    bank_path = os.path.join(LocalConf.CACHE_PATH, combined_file)
    for root, dirs, files in os.walk(path_run, topdown=False):
        if isinstance(files, list):
            for ff in files:
                if ".txt" in ff:
                    sxx.append(ff)
    bank = []
    for file_x in sxx:
        filepath = os.path.join(LocalConf.CACHE_PATH, folder_in_cache, file_x)
        io_source = open(filepath, 'r')
        lines = io_source.readlines()
        io_source.close()
        lines1 = lines[-1]
        lines[-1] = lines1 + "\n"
        bank += lines

    tl = len(bank)
    bank[-1] = bank[-1].replace("\n", "")
    print(f"total lines {tl}")
    io_source = open(bank_path, 'w')
    io_source.writelines(bank)
    io_source.close()
    print("checking for each line")
    io_source = open(bank_path, 'r')
    bank_lines = io_source.readlines()
    io_source.close()
    for e in bank_lines:
        words = e.split(" ")
        word_count = len(words)
        assert word_count == 12
    print("all testings are completed.")


def process_random_order(path: str, from_encryption_file: bool = False):
    """
    process and randomize the existing pass file from
    1) not encrpyted format
    2) encrpyted format
    """
    io_source = open(path, 'r')
    if from_encryption_file is True:
        folder, file = os.path.split(path)
        file2 = f"{file}_"
        decrypted_io = open(os.path.join(folder, file2), 'w')
        test_crt = Crypt()
        content = io_source.read()
        io_source.close()
        dec_content = test_crt.decrypt(content, LocalConf.DATA_SALT)
        decrypted_io.write(dec_content)
        decrypted_io.close()
        decrypted_io = open(os.path.join(folder, file2), 'r')
        lines = decrypted_io.readlines()
        decrypted_io.close()
    else:
        lines = io_source.readlines()
        io_source.close()

    # Shuffle the lines
    lines1 = lines[-1]
    lines[-1] = lines1 + "\n"
    random.shuffle(lines)
    tl = len(lines)
    lines[-1] = lines[-1].replace("\n", "")

    if from_encryption_file is False:
        io_source = open(path, 'w')
        io_source.writelines(lines)
        io_source.close()
        print(f"total random lines {tl}")
    else:
        test_crt = Crypt()
        folder, file = os.path.split(path)
        file2 = f"{file}_"
        decrypted_io = open(os.path.join(folder, file2), 'r')
        enc_content = test_crt.encrypt(decrypted_io.read(), LocalConf.DATA_SALT)
        decrypted_io.close()
        os.remove(os.path.join(folder, file2))
        io_source = open(path, 'w')
        io_source.writelines(enc_content)
        io_source.close()
        print(f"encryption file {file2} that has random lines of {tl}")


def readfiles(required_format: str) -> list[str]:
    """
    read the files in the file system in container and randomize the order from the given instructions
    can accept the file required format or custom format of the pass files
    """
    pass_file_list = []
    pass_file_list2 = []
    possible_folders = ["cache", "/home/galxe/cache"]
    while True:
        try:
            use_folder = ""
            for e in possible_folders:
                if isdir(e) is True:
                    use_folder = e
                    break
            source_path = os.path.join(f"./{use_folder}")
            for root, dirs, files in os.walk(source_path, topdown=False):
                if isinstance(files, list):
                    for ff in files:
                        if (".txt" in ff and required_format in ff) or ".ks" in ff or ".kz" in ff:
                            pass_file_list.append(ff)

            for f in pass_file_list:
                if os.path.exists(os.path.join(source_path, f)) is True:
                    pass_file_list2.append(f)

            if len(pass_file_list2) == 0:
                print("Sorry, no pass files found.")
                time.sleep(30)
                exit(3)
            else:
                pass_file_list2 = list(set(pass_file_list2))
                print("Pass files found")
                random.shuffle(pass_file_list2)
                print(pass_file_list2)
            return pass_file_list2
        except FileNotFoundError:
            continue


def readxclashconf() -> list:
    possible_folders = ["xclash", "xclashpro", "clashconf", "clashpro", "proxyclashagenx"]
    clash_confs = []
    clash_conf_paths = []
    while True:
        use_folder = ""
        for e in possible_folders:
            if isdir(e) is True:
                use_folder = e
                break
        source_path = os.path.join(f"./{use_folder}")
        for root, dirs, files in os.walk(source_path, topdown=False):
            if isinstance(files, list):
                for ff in files:
                    if ".yml" in ff:
                        clash_confs.append(ff)

        for x in clash_confs:
            source_x = os.path.join(source_path, x)
            if os.path.isfile(source_x):
                clash_conf_paths.append(source_x)
        break

    return clash_conf_paths


def remove_escape_sequences(string):
    return string.encode('utf-8').decode('unicode_escape')


def readconf(file_name: str, required_values: list[str]) -> dict:
    """
    reading the external configuration file in json format.
    find the configuration in the cache folder or other sources
    """
    tries = 0
    config = None
    possible_folders = ["scan_log", "app", "config", "cache"]
    while True:
        try:
            use_folder = ""
            for e in possible_folders:
                if isdir(e) is True:
                    use_folder = e
                    break
            source_path = os.path.join(f"./{use_folder}", file_name)
            if os.path.isfile(source_path):
                try:
                    config = json.load(open(source_path, 'r'))
                except json.decoder.JSONDecodeError:
                    io = open(source_path, 'r')
                    content = io.read()
                    io.close()
                    content = remove_escape_sequences(content)
                    config = json.loads(content)
            else:
                logging.error(
                    f"configuration file is not found. {source_path} please check with the directory settings")
                exit(404)

            if isinstance(config, dict):
                missing_values = [value for value in required_values if config[value] is None]
                if len(missing_values) > 0:
                    logging.error(
                        f'The following environment values are missing in your .env: {", ".join(missing_values)}')
                    exit(405)

            return config

        except FileNotFoundError:
            print("try again.. read files")
            tries += 1
            if tries > 5:
                logging.error(f"tried {tries} times to find the file and still not found.")
                exit(404)
            continue


def read_file_lines(filename: str) -> list:
    content_line = []
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            tmp = content.strip().replace("\n", "")
            content_line.append(tmp)
        fp.close()
    return content_line


def read_file_lines_from_encryption(filename: str) -> list:
    test_crpt = Crypt()
    io = open(filename, 'r')
    test_line = test_crpt.decrypt(io.read(), LocalConf.DATA_SALT)
    content_line = test_line.split("\n")
    t = datetime.datetime.now()
    print(f"Reading encrypt file {filename} {str(t)}")
    total = len(content_line)
    print("Total Lines", total)
    return content_line


def read_file_at_line(filename: str, line: int) -> str:
    content_line = ""
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            if count == line:
                content_line = content.strip().replace("\n", "")
        fp.close()
    return content_line


def read_file_total_lines(filename: str) -> int:
    t = datetime.datetime.now()
    print(f"count lines from metamask {filename} {str(t)}")
    with open(filename, 'r') as fp:
        for count, line in enumerate(fp):
            pass
        fp.close()
    print('Total Lines', count + 1)
    return count + 1


def find_version() -> str:
    f = codecs.open('version', 'r', 'utf-8-sig')
    new_ver = f.readline().strip()
    f.close()
    return new_ver


def json_save(content, tmp_file: str = "tmp.json"):
    my_str_as_bytes = None

    if isinstance(content, dict):
        my_str_as_bytes = str.encode(json.dumps(content))

    if isinstance(content, str):
        my_str_as_bytes = str.encode(content)

    if my_str_as_bytes is None:
        my_str_as_bytes = content

    path = os.path.join(LocalConf.CACHE_PATH, tmp_file)
    _save_bytes_c(my_str_as_bytes, path)


# Function to flatten JSON data
def flatten_json(data: dict, parent_key='', separator='.'):
    items = {}
    for key, value in data.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, separator))
        else:
            items[new_key] = value
    return items


def _save_bytes_c(content, file_name):
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


def _replace_func_format(c):
    if c == 'x':
        r = int(random.random() * 16)
        v = r if c == 'x' else (r & 0x3 | 0x8)
        return hex(v)[2:]
    else:
        return c


def gen_user_id():
    uuid = 'gxe_xxxxxxxx'
    uuid = ''.join([_replace_func_format(c) for c in uuid])
    return uuid
