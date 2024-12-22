

"""def get_cookies(cj, ff_cookies):
    con = sqlite3.connect(ff_cookies)
    cur = con.cursor()
    cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
    for item in cur.fetchall():
        c = cookielib.Cookie(0, item[4], item[5],
            None, False,
            item[0], item[0].startswith('.'), item[0].startswith('.'),
            item[1], False,
            item[2],
            item[3], item[3]=="",
            None, None, {})
        print c
        cj.set_cookie(c)
"""

import glob
import os
import sqlite3
import sys

__version__ = "2016-01-14 jan  denis-bz-py t-online de"


def Usage():
    print
    "/.../cookies.sqlite not found"
    sys.exit(1)


def dollarstar(filename):
    """ expand $vars, * """
    filename = os.path.expandvars(filename)  # e.g. $HOME
    names = glob.glob(filename)  # -> [] or [name ...]
    return names[0] if len(names) > 0 else filename  # 2 or more ?


def run_find_cookie():
    if len(sys.argv) >= 2:
        sqldb = sys.argv[1]
    else:
        sqldb = dollarstar("$HOME/Library/Application Support/Firefox/Profiles/*/cookies.sqlite")

    if not os.path.isfile(sqldb):
        Usage()

    # ...............................................................................
    # Bind to the sqlite db and execute sql statements
    conn = sqlite3.connect(sqldb)
    cur = conn.cursor()
    try:
        data = cur.execute('select * from moz_cookies')
    except sqlite3.Error as e:
        print('Error {0}:'.format(e.args[0]))
        exit(1)

    mydata = data.fetchall()

    #  0  id
    #  1  baseDomain
    #  2  appId
    #  3  inBrowserElement
    #  4  name
    #  5  value
    #  6  host
    #  7  path
    #  8  expiry
    #  9  lastAccessed
    # 10  creationTime
    # 11  isSecure
    # 12  isHttpOnly

    # urls only, no datetimes --
    urls = sorted(set([item[1] for item in mydata]))
    for url in urls:
        print(url)
