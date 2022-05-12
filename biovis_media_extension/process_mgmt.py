# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import re
import os
import psutil
import signal
import logging
import subprocess
from biovis_media_extension.utils import (get_candidate_name, check_dir,
                                      copy_and_overwrite)


class Process:
    def __init__(self, command_dir=None, workdir='/tmp/', main_program_name='run.sh'):
        self.logger = logging.getLogger('biovis-media-extension.process_mgmt.Process')
        if command_dir:
            self.command_dir = command_dir
            command_dirname = os.path.basename(command_dir)

            self.workdir = os.path.join(workdir, '%s_%s' % (command_dirname, get_candidate_name()))
            self.main_program = os.path.join(self.workdir, main_program_name)
            self.logger.debug('Main program: %s' % self.main_program)
            self.logger.debug('Command directory: %s' % self.command_dir)
            self.logger.debug('Working directory: %s' % self.workdir)

    def _find_file(self, directory, file_pattern):
        all_files = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if re.match(file_pattern, filename):
                    all_files.append(os.path.join(root, filename))

        if len(all_files) > 0:
            return all_files[0]
        else:
            return None

    def _gen_config(self, dest_dir, **kwargs):
        from configparser import ConfigParser
        self.logger.debug('Plugin temp directory: %s' % dest_dir)
        config_file_path = self._find_file(dest_dir, r'^.*.ini$')
        self.logger.debug('Reading config file: %s' % config_file_path)
        cfg = ConfigParser()
        cfg.optionxform = str
        cfg.read(config_file_path)

        for key, value in kwargs.items():
            if cfg.has_option('data', key) and value:
                if os.path.isfile(value):
                    basename = os.path.basename(value)
                    copy_and_overwrite(value, os.path.join(dest_dir, basename), is_file=True)
                    cfg.set('data', key, basename)
                else:
                    cfg.set('data', key, value)

            if cfg.has_option('attributes', key) and value:
                cfg.set('attributes', key, value)

        config_file = os.path.basename(config_file_path)
        with open(os.path.join(dest_dir, config_file), 'w') as f:
            cfg.write(f)

    def _exist_command(self):
        if os.path.isfile(self.main_program):
            return True
        else:
            return False

    def _set_env(self):
        check_dir(self.workdir, skip=True)
        copy_and_overwrite(self.command_dir, self.workdir)

    def run_command(self, domain='127.0.0.1', port='8000', **kwargs):
        self._set_env()
        self._gen_config(self.workdir, **kwargs)
        self._exist_command()

        if domain != '127.0.0.1' or domain != 'localhost':
            domain = '0.0.0.0'
        else:
            domain = '127.0.0.1'

        shell_cmd = [self.main_program, '-d', self.workdir, '-p', str(port), '-H', domain]
        self.logger.debug('Shell command: %s' % str(shell_cmd))
        with open(os.path.join(self.workdir, 'log'), 'w') as logfile:
            process = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE,
                                       stdout=logfile,
                                       stderr=logfile)
        return process.pid

    def get_process(self, process_id):
        try:
            p = psutil.Process(process_id)
            return p
        except psutil.NoSuchProcess:
            self.logger.warning('No such process: %s' % process_id)
            return None

    def get_output(self, process_id):
        process = self.get_process(process_id)
        if process:
            workdir = process.cwd()
            logfile = os.path.join(workdir, 'log')
            if os.path.isfile(logfile):
                with open(logfile, 'r') as f:
                    return f.read()
            else:
                return None
        else:
            return None

    def stop_process(self, process_id):
        process = self.get_process(process_id)
        if process:
            process.terminate()

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
