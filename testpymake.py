#!/usr/bin/env python3.11
import base64

import os
import random
import zlib
from marshal import dumps
import shutil

# root_path = os.path.dirname(os.path.abspath(__file__))
# root_path = os.path.abspath(os.path.dirname(__file__))
# deployment
root_path = os.getcwd()
print(root_path)
DEBUG = False


def base36encode():
    alphabet = '19abcdefghijklmnopqrstuvwxyz'
    generated_characters = ''.join(random.choice(alphabet) for _ in range(10))
    return f"1.{generated_characters}"


def replacement(tmp: str, from_keyword: str, to_keyword: str) -> str:
    # from lib import cookie3
    tmp = tmp.replace(f'from {from_keyword} import', f'from {to_keyword} import')
    tmp = tmp.replace(f'from {from_keyword}.', f'from {to_keyword}.')
    tmp = tmp.replace(f'import {from_keyword}.', f'import {to_keyword}.')
    return tmp


def fix_imports_trim(fpath: str, tpath: str, file_name: str = ""):
    process_file = os.path.join(root_path, fpath)
    dest_file = os.path.join(root_path, tpath)
    fpath = fpath.split("/")[0]
    tpath = tpath.split("/")[0]
    with open(process_file, 'r') as fd:
        tmp = fd.read()
        tmp = replacement(tmp, fpath, tpath)
        fd.close()
        with open(dest_file, 'wb') as fd2:
            fd2.write(str.encode(tmp))
            fd2.close()


def makepy(py_filename: str, path_from: str = "lib", to_path: str = "dist"):
    out_filename = py_filename[:-3] + '_exe.py' if py_filename == "main.py" else py_filename
    if path_from.endswith(".py") and to_path.endswith(".py"):
        print(path_from, to_path, out_filename)
        dest_file = os.path.join(root_path, to_path)
        try:
            write_path = os.path.dirname(os.path.abspath(dest_file))
            fix_imports_trim(path_from, to_path, py_filename)
            if DEBUG is True:
                return

            process_1_file = os.path.join(write_path, py_filename)
            level_1f_pyc = os.path.join(write_path, 'lv1')
            level_2f_pyc = os.path.join(write_path, 'lv2')
            level_3f_pyc = os.path.join(write_path, 'lv3')
            level_2_b = Rcompile(process_1_file)
            WriteStateInfoFile(level_2_b, level_2f_pyc)
            level_3_b = Rcompile(level_2f_pyc)
            WriteStateInfoFile(level_3_b, level_3f_pyc)
            level_4_b = Rcompile(level_3f_pyc)
            WriteStateInfoFile(level_4_b, level_1f_pyc)
            level_5_b = Rcompile(level_1f_pyc)
            WriteStateInfoFile(level_5_b, level_2f_pyc)
            level_6_b = Rcompile(level_2f_pyc)
            ObFile(level_6_b, dest_file)
            demov([level_1f_pyc, level_3f_pyc, level_2f_pyc])
        except OSError:
            fix_imports_trim(path_from, to_path, py_filename)
            print("err")
    else:
        if os.path.exists(to_path) is False:
            os.mkdir(to_path)

        dest_file = os.path.join(root_path, to_path)
        write_path = os.path.abspath(dest_file)
        dest_file = os.path.join(root_path, out_filename)
        src_file = os.path.join(root_path, py_filename)
        process_1_file = os.path.join(write_path, 'lvl2.py')
        level_1f_pyc = os.path.join(write_path, 'lv1')
        level_2f_pyc = os.path.join(write_path, 'lv2')
        level_3f_pyc = os.path.join(write_path, 'lv3')
        tmp = Rfile(src_file)

        tmp = replacement(tmp, path_from, to_path)

        if DEBUG is True:
            print(path_from, to_path)
            obSaveEile(dest_file, tmp)
            return

        level_1_b = compile(tmp, "", "exec")
        WriteStateInfoFile(level_1_b, level_1f_pyc)
        level_2_b = Rcompile(level_1f_pyc)
        WriteStateInfoFile(level_2_b, level_2f_pyc)
        level_3_b = Rcompile(level_2f_pyc)
        WriteStateInfoFile(level_3_b, level_3f_pyc)
        level_4_b = Rcompile(level_3f_pyc)
        WriteStateInfoFile(level_4_b, level_1f_pyc)
        level_5_b = Rcompile(level_1f_pyc)
        WriteStateInfoFile(level_5_b, level_2f_pyc)
        level_6_b = Rcompile(level_2f_pyc)
        ObFile(level_6_b, dest_file)
        demov([process_1_file, level_1f_pyc, level_3f_pyc, level_2f_pyc])


def obSaveEile(file_op: str, tmp: str):
    with open(file_op, "w+") as d:
        d.write(tmp)
        d.close()


def Rcompile(file):
    with open(file, "r") as io:
        data = io.read()
        io.close()
        return compile(data, base36encode(), 'exec')


def Rfile(file):
    with open(file, "r") as io:
        data = io.read()
        io.close()
        print(data)
        return data


def ObFile(level_b: bytes, level_file: str):
    b = zlib.compress(dumps(level_b))
    c = base64.b64encode(b).decode()
    level = b'from marshal import loads as w\nfrom base64 import b64decode as d\nfrom zlib import decompress as z\nexec(w(z(d(%r))))' % c
    level_io = open(level_file, 'wb')
    level_io.write(level)
    level_io.close()
    print("Saving obfuscated python too %s" % level_file)


def demov(s: list):
    for t in s:
        if os.path.exists(t):
            os.remove(t)
            d = os.path.dirname(t)
            check = os.path.join(d, "__pycache__")
            print(check)
            if os.path.exists(t):
                os.rmdir(check)


def WriteStateInfoFile(code_module, level_file: str):
    level = b'from marshal import loads\nexec(loads(%r))' % dumps(code_module)
    level_io = open(level_file, 'wb')
    level_io.write(level)
    level_io.close()


EXCLUSION = [".DS_Store", "__pycache__"]
TRANS = ["__init__.py"]


def scan_all(from_dir: str = "lib", to_lib: str = "dist"):
    if os.path.exists(to_lib) is False:
        os.mkdir(to_lib)

    for root, dirs, files in os.walk(from_dir, topdown=True):
        dest_path = root.replace(from_dir, to_lib)
        if os.path.exists(dest_path) is False:
            os.mkdir(dest_path)

        for name in files:
            from_path = os.path.join(root, name)
            to_path = os.path.join(dest_path, name)
            if name.endswith(".py") is True:
                if name in TRANS:
                    # print(from_path, to_path, "trans")
                    fix_imports_trim(from_path, to_path, name)
                else:
                    # print("make py")
                    makepy(name, from_path, to_path)
                    # fix_imports_trim(from_path, to_path, name)
            else:
                if name not in EXCLUSION and not name.endswith(".pyc"):
                    shutil.copyfile(from_path, to_path)

            # print(os.path.join(root, name))


if __name__ == '__main__':
    if os.path.exists("main.py") is False:
        print("main.py is not found.")
        exit(0)
    if os.path.exists("lib") is False:
        print("folder lib is not found.")
        exit(0)
    makepy("main.py")
    scan_all()
