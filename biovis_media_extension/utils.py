# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import shutil
import logging
import socket
from contextlib import closing

from random import Random as _Random
import _thread
_allocate_lock = _thread.allocate_lock
_once_lock = _allocate_lock()
_name_sequence = None

logger = logging.getLogger(__name__)


class BashColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    SUCCESS = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    DANGER = '\033[91m'   # Red
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INFO = '\033[30m'     # Black

    @classmethod
    def _get_color(cls, color_name):
        color_dict = {
            'SUCCESS': BashColors.SUCCESS,
            'INFO': BashColors.INFO,
            'WARNING': BashColors.WARNING,
            'DANGER': BashColors.DANGER,
            'UNDERLINE': BashColors.UNDERLINE,
            'BOLD': BashColors.BOLD,
            'BLUE': BashColors.OKBLUE
        }
        return color_dict.get(color_name.upper(), BashColors.INFO)

    @classmethod
    def get_color_msg(cls, color_name, msg):
        return cls._get_color(color_name) + msg + BashColors.ENDC

    @classmethod
    def print_color(cls, color_name, msg):
        print(cls._get_color(color_name) + msg + BashColors.ENDC)


def copy_and_overwrite(from_path, to_path, is_file=False, force_remove=True):
    if os.path.isfile(to_path) and force_remove:
        os.remove(to_path)

    if os.path.isdir(to_path) and force_remove:
        shutil.rmtree(to_path)

    try:
        if is_file and os.path.isfile(from_path):
            shutil.copy2(from_path, to_path)
        elif os.path.isdir(from_path):
            shutil.copytree(from_path, to_path)
    except Exception as err:
        logger.debug('Copy %s to %s error: %s' % (from_path, to_path, str(err)))


def print_obj(str):
    try:  # For Python2.7
        print(unicode(str).encode('utf8'))
    except NameError:  # For Python3
        print(str)


def check_dir(path, skip=False, force=True):
    """
    Check whether path exists.

    :param path: directory path.
    :param skip: Boolean, Raise exception when skip is False and directory exists.
    :param force: Boolean, Force to make directory when directory doesn't exist?
    :return:
    """
    if not os.path.isdir(path):
        if force:
            os.makedirs(path)
        else:
            raise Exception("%s doesn't exist." % path)
    elif not skip:
        raise Exception("%s exists" % path)


class _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.
    _RandomNameSequence is an iterator."""

    characters = ("abcdefghijklmnopqrstuvwxyz" +  # noqa
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +  # noqa
                  "0123456789_")

    def __init__(self):
        self.mutex = _allocate_lock()
        self.normcase = os.path.normcase

    @property
    def rng(self):
        cur_pid = os.getpid()
        if cur_pid != getattr(self, '_rng_pid', None):
            self._rng = _Random()
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def next(self):
        m = self.mutex
        c = self.characters
        choose = self.rng.choice

        m.acquire()
        try:
            letters = [choose(c) for dummy in "123456"]
        finally:
            m.release()

        return self.normcase(''.join(letters))


def get_candidate_name():
    """Common setup sequence for all user-callable interfaces."""

    global _name_sequence
    if _name_sequence is None:
        _once_lock.acquire()
        try:
            if _name_sequence is None:
                _name_sequence = _RandomNameSequence()
        finally:
            _once_lock.release()
    return _name_sequence.next()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_local_abs_fpath(path):
    current_path = os.environ.get('BIOVIS_CURRENT_FILE_PATH', os.getcwd())
    # May be current_path is a file path, but we need a directory.
    if os.path.isfile(current_path):
        current_path = os.path.dirname(current_path)

    # The path is an absolute path when os.path.abspath(path) == path.
    # We need to get the absolute path when the path is a relative path.
    if os.path.abspath(path) != path:
        real_path = os.path.abspath(os.path.join(current_path, path))
    else:
        real_path = os.path.abspath(path)

    if os.path.isfile(real_path) or os.path.isdir(real_path):
        path = real_path

    return path
