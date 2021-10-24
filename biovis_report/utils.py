# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import re
import os
import logging
import shutil
import psutil
import signal
import argparse
from datetime import datetime
from random import Random as _Random
import _thread

_allocate_lock = _thread.allocate_lock
_once_lock = _allocate_lock()
_name_sequence = None

logger = logging.getLogger('report.utils')


def get_resource_dir():
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, 'resources')


def check_plugin():
    try:
        import biovis_media_extension  # noqa
        return True
    except ImportError:
        msg = 'Use `pip install biovis_media_extension` to support report plugin.\n'
        logger.warning('Report plugin is not yet supported by biovis.\n%s' % msg)
        return False


def is_valid(path):
    """
    Integrates with ArgParse to validate a file path.

    :param path: Path to a file.
    :return: The path if it exists, otherwise raises an error.
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(
            ("{} is not a valid file/directory path.\n".format(path)))
    else:
        return path


def is_valid_url(url):
    pattern = r'(https?)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
    if re.match(pattern, url):
        return True
    else:
        return False


def get_copyright(site_author='biovis'):
    if not site_author:
        site_author = 'biovis'

    year = datetime.now().year
    copyright = 'Copyright &copy; {} {}, ' \
                'Powered by <a href="http://biovis.3steps.cn">' \
                'BioVis</a>.'.format(year, site_author.title())
    return copyright


def copy_and_overwrite(from_path, to_path, is_file=False, ignore_errors=True, ask=False):
    if ask:
        answer = ''
        while answer.upper() not in ("YES", "NO", "Y", "N"):
            answer = input("Remove %s, Enter Yes/No: " % to_path)  # noqa: python3

            answer = answer.upper()
            if answer == "YES" or answer == "Y":
                ignore_errors = True
            elif answer == "NO" or answer == "N":
                ignore_errors = False
            else:
                print("Please enter Yes/No.")

    if ignore_errors:
        # TODO: rmtree is too dangerous
        if os.path.isfile(to_path):
            os.remove(to_path)

        if os.path.isdir(to_path):
            shutil.rmtree(to_path)

    try:
        if is_file and os.path.isfile(from_path):
            parent_dir = os.path.dirname(to_path)
            # Force to make directory when parent directory doesn't exist
            os.makedirs(parent_dir, exist_ok=True)
            shutil.copy2(from_path, to_path)
        elif os.path.isdir(from_path):
            shutil.copytree(from_path, to_path)
    except Exception as err:
        logger.warning('Copy %s to %s error: %s' % (from_path, to_path, str(err)))


def clean_files(folder, skip=True):
    if os.path.isdir(folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                if not skip:
                    print(e)
    else:
        logger.debug("No such directory: %s" % folder)


def clean_temp(temp, dir=True):
    # Clean temp directory
    if dir:
        shutil.rmtree(temp, ignore_errors=True)
    else:
        try:
            os.remove(temp)
        except Exception:
            pass


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


class Process:
    def __init__(self):
        self.logger = logging.getLogger('biovis.utils.Process')

    def get_process(self, process_id):
        try:
            p = psutil.Process(process_id)
            return p
        except psutil.NoSuchProcess:
            self.logger.warning('No such process: %s' % process_id)
            return None

    def clean_processs(self):
        process_id = os.getpid()
        process = self.get_process(process_id)
        if process:
            self.kill_proc_tree(process_id)

    def kill_proc_tree(self, pid, sig=signal.SIGTERM, include_parent=False,
                       timeout=3, on_terminate=None):
        """Kill a process tree (including grandchildren) with signal
        "sig" and return a (gone, still_alive) tuple.
        "on_terminate", if specified, is a callabck function which is
        called as soon as a child terminates.
        """
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        children_pids = [child.pid for child in children]
        self.logger.debug('Kill process: %s and all children %s' % (pid, children_pids))
        try:
            for p in children:
                p.send_signal(sig)
            gone, alive = psutil.wait_procs(children, timeout=timeout,
                                            callback=on_terminate)
            return (gone, alive)
        except Exception as err:
            self.logger.debug('Kill all processes: %s' % str(err))
            return (None, None)


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
