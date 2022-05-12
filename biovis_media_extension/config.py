# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import logging
import configparser

logger = logging.getLogger(__name__)
CONFIG_FILES = ['~/.biovis/biovis.conf', '/etc/biovis.conf']


def getconf(config_files):
    for f in config_files:
        try:
            loc = os.path.expanduser(f)
        except KeyError:
            # os.path.expanduser can fail when $HOME is undefined and
            # getpwuid fails. See http://bugs.python.org/issue20164 &
            # https://github.com/kennethreitz/requests/issues/1846
            return

        if os.path.exists(loc):
            return loc


config = configparser.ConfigParser()

config_files = CONFIG_FILES
conf_path = getconf(config_files)


def check_oss_config():
    if access_key and access_secret and endpoint:
        return True
    else:
        raise Exception("You need to config oss section in biovis.conf")


if conf_path:
    config.read(conf_path, encoding="utf-8")

    # oss access_key and access_secret
    access_key = config.get('oss', 'access_key')
    access_secret = config.get('oss', 'access_secret')
    endpoint = config.get('oss', 'endpoint')

    check_oss_config()


def get_oss_bin():
    if sys.platform == 'darwin':
        oss_bin = os.path.join(os.path.dirname(
            __file__), "lib", 'ossutilmac64')
    else:
        oss_bin = os.path.join(os.path.dirname(__file__), "lib", 'ossutil64')
    return oss_bin
