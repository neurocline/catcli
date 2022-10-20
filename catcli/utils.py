"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2017, deadc0de6

helpers
"""

import os
import hashlib
import tempfile
import subprocess
import datetime

# local imports
from catcli.logger import Logger


def md5sum(path):
    '''calculate md5 sum of a file'''
    p = os.path.realpath(path)
    if not os.path.exists(p):
        Logger.err(f'\nmd5sum - file does not exist: {p}')
        return None
    try:
        with open(p, mode='rb') as f:
            d = hashlib.md5()
            while True:
                buf = f.read(4096)
                if not buf:
                    break
                d.update(buf)
            return d.hexdigest()
    except PermissionError:
        pass
    except OSError as e:
        Logger.err(f'md5sum error: {e}')
    return None


def size_to_str(size, raw=True):
    '''convert size to string, optionally human readable'''
    div = 1024.
    suf = ['B', 'K', 'M', 'G', 'T', 'P']
    if raw or size < div:
        return f'{size}'
    for i in suf:
        if size < div:
            return f'{size:.1f}{i}'
        size = size / div
    sufix = suf[-1]
    return f'{size:.1f}{sufix}'


def epoch_to_str(epoch):
    '''convert epoch to string'''
    if not epoch:
        return ''
    fmt = '%Y-%m-%d %H:%M:%S'
    t = datetime.datetime.fromtimestamp(float(epoch))
    return t.strftime(fmt)


def ask(question):
    '''ask the user what to do'''
    resp = input(f'{question} [y|N] ? ')
    return resp.lower() == 'y'


def edit(string):
    '''edit the information with the default EDITOR'''
    string = string.encode('utf-8')
    EDITOR = os.environ.get('EDITOR', 'vim')
    with tempfile.NamedTemporaryFile(prefix='catcli', suffix='.tmp') as f:
        f.write(string)
        f.flush()
        subprocess.call([EDITOR, f.name])
        f.seek(0)
        new = f.read()
    return new.decode('utf-8')
