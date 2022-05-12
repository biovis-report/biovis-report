# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import re
import uuid

import shutil
import hashlib
import requests
import logging
import collections
import pkg_resources
from biovis_media_extension.models import add_plugin, get_plugin
from biovis_media_extension.process_mgmt import Process
from biovis_media_extension.utils import (check_dir, copy_and_overwrite,
                                      BashColors, get_candidate_name,
                                      find_free_port, get_local_abs_fpath)
from biovis_media_extension.file_mgmt import run_copy_files, get_oss_fsize
from biovis_media_extension.request_mgmt import requests_retry_session


class Reader:
    def __init__(self, markdown_file):
        self.markdown_file = markdown_file

    def get_raw_content(self):
        warn_content = 'No manual entry, please contact the developer.'
        if os.path.isfile(self.markdown_file):
            with open(self.markdown_file, 'r') as f:
                content = f.read()
                if len(content) != 0:
                    return content
        return warn_content

    def _render_html(self, help_doc):
        from jinja2 import Environment, FileSystemLoader
        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('help_doc_template.html')
        return template.render(help_doc=help_doc)

    def get_html(self):
        from markdown import markdown

        content = self.get_raw_content()
        config = {
            'pymdownx.inlinehilite': {
                'style_plain_text': True
            }
        }
        extensions = ['pymdownx.inlinehilite', 'admonition', 'def_list',
                      'sane_lists', 'pymdownx.superfences',
                      'pymdownx.highlight']
        content_html = markdown(content, extensions=extensions,
                                extension_configs=config)
        html = self._render_html(content_html)
        return html


class BasePlugin:
    """
    Plugin class is initialized by plugin args from markdown.
    Plugin args: @plugin_name(arg1=value, arg2=value, arg3=value)

    :Examples:
    1. render mode
    2. bokeh static mode
    3. plotly static mode
    4. server mode
    5. multiqc mode
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize BasePlugin class.

        :param: context: a dict that contains all plugin arguments.
        :param: net_dir: plugin used it to get relative network path for all files that are needed by html. if net_dir is None, plugin will upload all files to qiniu and get a qiniu url.
        :param: sync_oss: whether sync oss.
        :param: sync_http: whether sync http.
        :param: sync_ftp: whether sync ftp.
        :param: file_size: file size(MB).
        """
        print("BasePlugin: %s, %s" % (str(args), str(kwargs)))
        self.net_dir = kwargs.get('net_dir', None)
        self.sync_oss = kwargs.get('sync_oss', True)
        self.sync_http = kwargs.get('sync_http', True)
        self.sync_ftp = kwargs.get('sync_ftp', True)
        self.target_fsize = kwargs.get('target_fsize') or 10
        self.domain = kwargs.get('domain', '127.0.0.1')
        self.protocol = kwargs.get('protocol', 'http')
        self.enable_iframe = kwargs.get('enable_iframe', True)
        self.wait_server_seconds = kwargs.get('wait_server_seconds') or 5
        self.backoff_factor = kwargs.get('backoff_factor') or 3
        # Parse args from markdown new syntax. e.g.
        # @scatter_plot(a=1, b=2, c=3)
        # kwargs = {'a': 1, 'b': 2, 'c': 3}
        self._context = kwargs.get('context', {})

        self.logger = logging.getLogger('biovis.biovis-media-extension.plugin')
        if self.net_dir:
            temp_dir = os.path.join(self.net_dir, '.biovis-media-extension')
        else:
            temp_dir = os.path.join('/tmp', 'biovis-media-extension')
            self.logger.warn("No net_dir, so use temp directory(%s)." % temp_dir)
            # Clean up the temp directory
            # TODO: rmtree will cause other biovis process failed, how to solve it?
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.plugin_db = os.path.join(temp_dir, 'plugin.db')

        self.tmp_plugin_dir = os.path.join(temp_dir, str(uuid.uuid1()))
        # Fix bug: use plugin name as global dir name instead of random file name
        #          for saving all files from a plugin.
        self.plugin_data_dir = os.path.join(self.tmp_plugin_dir, self.plugin_name)
        check_dir(self.plugin_data_dir, skip=True)

        self.ftype2dir = {
            'css': os.path.join(self.plugin_data_dir, 'css'),
            'javascript': os.path.join(self.plugin_data_dir, 'js'),
            'js': os.path.join(self.plugin_data_dir, 'js'),
            'image': os.path.join(self.plugin_data_dir, 'images'),
            'font': os.path.join(self.plugin_data_dir, 'fonts'),
            'data': os.path.join(self.plugin_data_dir, 'data'),
            'context': os.path.join(self.plugin_data_dir, 'context'),
            'html': os.path.join(self.plugin_data_dir, 'html'),
        }

        for dir in self.ftype2dir.values():
            check_dir(dir, skip=True, force=True)

        # The target_id will help to index html component position.
        self.target_id = str(uuid.uuid1())

        # The index db for saving key:real_path pairs.
        self._index_db = [{
            'type': 'directory',
            'key': key,
            'value': value
        } for key, value in self.ftype2dir.items()]

        # All plugin args need to check before next step.
        self._wrapper_check_args()

        # rendered js code
        self._rendered_js = []

        # Set reader for README.md
        self.reader = self.set_help()

    @classmethod
    def get_ftype(cls, fext):
        """
        Set supported file type.
        """
        css_lst = ('css',)
        js_lst = ('js', 'javascript')
        image_lst = ('png', 'jpg', 'svg')
        font_lst = ('eot', 'ttf', 'woff', 'woff2', 'otf')
        data_lst = ('csv', 'rds', 'tsv')

        if fext in css_lst or fext.upper() in css_lst:
            return 'css'
        elif fext in js_lst or fext.upper() in js_lst:
            return 'js'
        elif fext in image_lst or fext.upper() in image_lst:
            return 'image'
        elif fext in font_lst or fext.upper() in font_lst:
            return 'font'
        elif fext in data_lst or fext.upper() in data_lst:
            return 'data'

    def _find_files(self, directory, file_pattern=None, exclude_pattern=None):
        all_files = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if exclude_pattern and re.match(exclude_pattern, filename):
                    continue

                if file_pattern and re.match(file_pattern, filename):
                    all_files.append(os.path.join(root, filename))

                if file_pattern is None:
                    all_files.append(os.path.join(root, filename))

        return all_files

    def _render_html(self, templ_dir, templ_file, cache=True, file_pattern=None,
                     exclude_pattern=None, **render_kwargs):
        from jinja2 import Environment, FileSystemLoader, contextfilter

        if cache:
            all_files = self._find_files(templ_dir, file_pattern=file_pattern,
                                         exclude_pattern=exclude_pattern)
            self.logger.debug('Get template files: %s' % str(all_files))
            for file in all_files:
                # e.g. css/bootstrap.min.css
                key = file.replace(templ_dir, '').strip('/')
                _, file_ext = os.path.splitext(key)
                ftype = self.get_ftype(file_ext.strip('.'))
                # Skip not supported file type.
                if ftype:
                    self.set_index(key, file, ftype=ftype)
                    net_path = self.get_net_path(key)
                    self.logger.debug("Cache %s" % net_path)

        @contextfilter
        def url_filter(context, value):
            """ A Template filter to normalize URLs. """
            # Need to add /, otherwise browser will add base url as a prefix.
            # e.g. data-table-js/html/data-table-js/css/font-awesome.min.css
            net_path = self.get_net_path(value)
            self.logger.debug("Filter url %s to %s" % (value, net_path))
            return net_path

        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), templ_dir)
        env = Environment(loader=FileSystemLoader(template_dir))
        env.filters['url'] = url_filter
        template = env.get_template(templ_file)
        return template.render(**render_kwargs)

    @classmethod
    def set_help(cls):
        help_md_file = os.path.join(cls.plugin_dir, 'README.md')
        if os.path.isfile(help_md_file):
            reader = Reader(help_md_file)
        else:
            reader = None
        return reader

    @classmethod
    def show_help(cls, ftype='markdown', output=''):
        """
        :param: ftype: markdown, html, browser
        """
        reader = cls.set_help()
        if reader:
            if ftype.lower() == 'markdown':
                content = reader.get_raw_content()
            elif ftype.lower() == 'html':
                content = reader.get_html()
            elif ftype == 'browser':
                import webbrowser
                import tempfile
                content = reader.get_html()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                # Fix bug: TypeError: a bytes-like object is required, not 'str'
                temp_file.write(content.encode())
                temp_file.close()
                webbrowser.open_new('file://%s' % temp_file.name)
                # No output to save or flush.
                print("Please check your browser for help doc.")
                return
        else:
            content = 'No manual entry for %s' % cls.plugin_name

        if output:
            with open(output, 'w') as f:
                f.write(content)
        else:
            print(content)
            sys.stdout.flush()

    @classmethod
    def show_version(cls):
        import imp
        version_file = os.path.join(cls.plugin_dir, 'version.py')
        if os.path.join(version_file):
            m = imp.load_source('version', version_file)
            try:
                print("%s %s" % (cls.plugin_name, m.get_version()))
            except Exception:
                print("Unknown version")
        else:
            print("Unknown version")

    @property
    def plugin_dir(self):
        raise NotImplementedError('BasePlugin Subclass must override plugin_dir attribute.')

    @property
    def plugin_name(self):
        raise NotImplementedError('BasePlugin Subclass must override plugin_name attribute.')

    @property
    def is_server(self):
        raise NotImplementedError('BasePlugin Subclass must override is_server attribute.')

    def get_file_size(self, path, protocol='http'):
        # TODO: handle error
        if protocol == 'http' or protocol == 'https':
            content_length = requests.get(path, stream=True).headers['Content-length']
        elif protocol == 'oss':
            content_length = get_oss_fsize(path)  # MB
        elif protocol == 'file':
            if os.path.isfile(path):
                content_length = os.path.getsize(path)
            else:
                # If path does't exist, skip it by giving a huge value.
                content_length = 1000000000000000000000000000
        elif protocol == 'ftp':
            # TODO: support to get file size(ftp).
            content_length = 0

        self.logger.debug('File Size(%s Bytes): %s' % (path, content_length))
        file_size = int(content_length) / (1024 * 1024)  # MB
        return file_size

    def _fsize_is_ok(self, path, target_value, protocol='http'):
        file_size = self.get_file_size(path, protocol=protocol)
        self.logger.debug("Path: %s, target_value: %s, file_size: %s, "
                          "protocol: %s" % (path, target_value, file_size, protocol))
        if file_size < target_value:
            return True
        else:
            return False

    def add_file_type(self, ftype):
        dest_dir = os.path.join(self.plugin_data_dir, ftype)
        check_dir(dest_dir, skip=True, force=True)
        self.ftype2dir.update({
            ftype: dest_dir
        })

    def _wrapper_check_args(self):
        """
        Unpack context into keyword arguments of check_plugin_args method.
        """
        self.check_plugin_args(**self._context)

    def check_plugin_args(self, **kwargs):
        """
        All plugin args is holded by self._context. you need to check all plugin args when inherit Plugin class.
        """
        raise NotImplementedError('You need to reimplement check_plugin_args method.')

    def filter_ctx_files(self):
        """
        Filter context for getting all files.
        """
        files = []
        file_pattern = r'^(/)?([^/\0]+(/)?)+$'
        ftp_pattern = r'^ftp://.*$'
        http_pattern = r'^(http|https)://.*$'
        oss_pattern = r'^oss://.*$'

        for key, value in self._context.items():
            if isinstance(value, str):
                # We need to cache all related files before render markdown files.
                # e.g. files in context, _prepare_js(), _prepare_css(), external_data()
                # Only files in context are from end user and the file path may be a relative path,
                # so need to get the real absolute path.
                abs_path = get_local_abs_fpath(value)
                if re.match(file_pattern, str(abs_path)) and os.path.isdir(abs_path):
                    files.append({
                        'value': abs_path,
                        'key': key,
                        'type': 'context'
                    })

                if re.match(file_pattern, str(abs_path))\
                   and self._fsize_is_ok(abs_path, self.target_fsize, 'file'):
                    # The path of file in context may be a relative path,
                    # so we need to get real path firstly.
                    files.append({
                        'value': abs_path,
                        'key': key,
                        'type': 'context'
                    })

                if self.sync_ftp and re.match(ftp_pattern, str(value))\
                   and self._fsize_is_ok(value, self.target_fsize, 'ftp'):
                    files.append({
                        'value': value,
                        'key': key,
                        'type': 'context'
                    })

                if self.sync_http and re.match(http_pattern, str(value))\
                   and self._fsize_is_ok(value, self.target_fsize, 'http'):
                    files.append({
                        'value': value,
                        'key': key,
                        'type': 'context'
                    })

                if self.sync_oss and re.match(oss_pattern, str(value))\
                   and self._fsize_is_ok(value, self.target_fsize, 'oss'):
                    files.append({
                        'value': value,
                        'key': key,
                        'type': 'context'
                    })

        self.logger.debug("Filter Context Files: %s" % str(files))
        return files

    @property
    def context(self):
        return self._context

    @property
    def index_db(self):
        """
        Return index db's records.
        """
        return self._index_db

    def get_index(self, key):
        """
        Get record index from index db.
        """
        for idx, dic in enumerate(self._index_db):
            if dic['key'] == key:
                return idx
        return -1

    def get_value_by_idx(self, idx):
        """
        Get value by using record index from index db.
        """
        if idx >= 0:
            return self._index_db[idx].get('value')

    def set_value_by_idx(self, idx, value):
        if idx >= 0 and idx < len(self._index_db):
            self._index_db[idx].update({
                'value': value
            })

    def search(self, key):
        """
        Search index db by using key.
        """
        # Bug: next func just return one value,
        # so you need to make sure that the key in self._index_db is unique.
        return next((item for item in self._index_db if item["key"] == key), None)

    def _get_dest_dir(self, ftype):
        """
        Get the plugin data directory.
        """
        dest_dir = self.ftype2dir.get(ftype.lower())
        return dest_dir

    def set_index(self, key, path, ftype='css'):
        """
        Add a record into index db. All files from plugin arguments will be autosaved and indexed. Other files must be saved and indexed manually by plugin developer.

        :param key: index key, plugin developer can get the real path or network url of the file by using the key.
        :param path: the path of a file that is needed to cache and index.
        :param ftype: file type, it will determin where the file will be saved.
        """
        if self.search(key):
            color_msg = BashColors.get_color_msg('WARNING', 'The key (%s) is inside of index db. '
                                                 'The value will be updated by new value.' % key)
            self.logger.warning(color_msg)
            idx = next((index for (index, d) in enumerate(self._index_db) if d["key"] == key), None)
            self._index_db[idx] = {
                'type': ftype,
                'key': key,
                'value': path
            }
        else:
            pattern = r'^%s.*' % self.plugin_data_dir
            matched = re.match(pattern, path)
            # Save file when the file is not in plugin_data_dir.
            if not matched:
                self.logger.debug('set_index: %s, %s, %s, %s' % (key, path, ftype, pattern))
                self._save_file(key, path, ftype=ftype)
            else:
                self._index_db.append({
                    'type': ftype,
                    'key': key,
                    'value': path
                })

    def _save_file(self, key, path, ftype='css'):
        """
        Copy the file to plugin data directory.
        """
        dest_dir = self._get_dest_dir(ftype)
        # TODO: how to distinguish file path from string? We can not simply raise NotImplementedError when can not get dest_dir by using ftype.
        if not dest_dir:
            raise NotImplementedError("Can't support the file type: %s" % ftype)

        if os.path.isfile(path):
            is_file = True
            net_path = 'file://' + path
        elif os.path.isdir(path):
            is_file = False
            net_path = 'file://' + path
        else:
            net_path = path

        self.logger.debug('_save_file file_path: %s' % net_path)
        matched = re.match(r'^(https|http|file|ftp|oss)://.*$', net_path)
        if matched:
            protocol = matched.groups()[0]
            dest_filepath = os.path.join(dest_dir, os.path.basename(path))

            self.set_index(key, dest_filepath, ftype=ftype)
            if protocol == 'file':
                # TODO: May be copy_and_overwrite will make some mistakes.
                copy_and_overwrite(path, dest_filepath, is_file=is_file)
            elif protocol == 'oss':
                run_copy_files(path, dest_filepath, self.plugin_data_dir,
                               recursive=False, silent=True)
            elif protocol == 'http' or protocol == 'https':
                r = requests.get(net_path)
                if r.status_code == 200:
                    with open(dest_filepath, "wb") as f:
                        f.write(r.content)
                else:
                    self.logger.debug('No such file: %s' % path)
            elif protocol == 'ftp':
                # TODO: support to save ftp file.
                pass
        else:
            self.logger.debug('No such file: %s' % path)

    def external_data(self):
        """
        Adding external data files.

        :return: file dict, such as {'idx_key': 'filepath'}
        """
        pass

    def external_css(self):
        """
        Adding external css files.

        :return: file list, such as [{'idx_key': 'filepath'}]
        """
        pass

    def external_javascript(self):
        """
        Adding external javascript files.

        :return: file list, such as [{'idx_key': 'filepath'}]
        """
        pass

    def inject(self, net_path, ftype='css'):
        """
        Inject js and css into document.
        """
        if ftype not in ('css', 'js', 'javascript'):
            self.logger.warning('inject %s error, %s is not supported.' % (net_path, ftype))
        else:
            # checkDeps is defined in load-script.js(see mkdocs theme)
            script = "<script>checkDeps('%s', '%s', false)</script>" % (net_path, ftype)
            self._rendered_js.append(script)

    def _get_index_lst(self, external_files, ftype):
        try:
            idx_dict = []
            if isinstance(external_files, dict):
                for key, value in external_files.items():
                    idx_dict.append({
                        'key': key,
                        'value': value,
                        'type': ftype
                    })
            elif isinstance(external_files, list):
                for idx, value in enumerate(external_files):
                    idx_dict.append({
                        'key': list(value.keys())[0],
                        'value': list(value.values())[0],
                        'type': ftype
                    })
            return idx_dict
        except Exception as err:
            self.logger.warning(str(err))
            raise Exception('External file must be a dict that contains'
                            ' key: value or a list that contains {key: value}.')

    def _prepare_js(self):
        javascript = self._get_index_lst(self.external_javascript(), 'js')
        # TODO: async加速?
        for item in javascript:
            self.set_index(item.get('key'), item.get('value'), item.get('type'))
            self.logger.debug('index_db: %s, context: %s' % (self._index_db, self.context))
            net_path = self.get_net_path(item.get('key'))
            _, file_ext = os.path.splitext(net_path)
            # media files don't need to inject, e.g. images/tff
            if file_ext == '.js' or file_ext == '.javascript':
                self.inject(net_path, ftype='js')

    def set_default_static(self):
        default_css = os.path.join(os.path.dirname(__file__), 'static', 'default.css')
        css_lst = [{
            'default_css': default_css
        }]
        css = self._get_index_lst(css_lst, 'css')
        # TODO: async加速?
        for item in css:
            self.set_index(item.get('key'), item.get('value'), item.get('type'))
            self.inject(self.get_net_path(item.get('key')), ftype='css')

    def _prepare_css(self):
        css = self._get_index_lst(self.external_css(), 'css')

        # TODO:
        # 1. async加速?
        # 2. support to cache directory?
        for item in css:
            self.set_index(item.get('key'), item.get('value'), item.get('type'))
            net_path = self.get_net_path(item.get('key'))
            _, file_ext = os.path.splitext(net_path)
            # media files don't need to inject, e.g. images/tff
            if file_ext == '.css':
                self.inject(net_path, ftype='css')

        self.logger.debug('index_db: %s, context: %s, css: %s' % (self._index_db, self.context, css))

    def prepare(self):
        """
        One of stages: copy all dependencies to plugin data directory.
        """
        self.set_default_static()
        self._prepare_css()
        self._prepare_js()

        data = self._get_index_lst(self.external_data(), 'data')
        context_files = self.filter_ctx_files()

        files = data + context_files

        # TODO: async加速?
        for item in files:
            self.set_index(item.get('key'), item.get('value'), item.get('type'))

    def multiqc(self, analysis_dir):
        import sys
        from subprocess import CalledProcessError, PIPE, Popen

        output_dir = self._get_dest_dir('html')
        output_fname = 'multiqc_report_%s' % get_candidate_name()
        report_output = '%s/%s.html' % (output_dir, output_fname)

        check_dir(output_dir, skip=True, force=True)
        multiqc_cmd = ['multiqc', '-o', output_dir, '--filename',
                       output_fname, analysis_dir]
        # write metadata to plugin.db
        metadata = {}
        metadata['name'] = self.plugin_name
        metadata['command'] = '@{}({})'.format(self.plugin_name, self._get_args(**self.context))
        metadata['command_md5'] = self._md5(metadata['command'])
        metadata['is_server'] = self.is_server
        plugin = get_plugin(metadata['command_md5'], self.plugin_db)
        if not plugin:
            try:
                process = Popen(multiqc_cmd, stdout=PIPE)
                while process.poll() is None:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    self.logger.info(output.strip())
                    sys.stdout.flush()
                    process.poll()

                metadata['access_url'] = report_output
                add_plugin(**metadata, plugin_db=self.plugin_db)

                self.logger.info("Running multiqc plugin (%s) successfully, "
                                 "Output in %s.\n" % (self.plugin_name, report_output))
                return report_output
            except CalledProcessError as e:
                self.logger.critical(e)
                return None
        else:
            self.logger.info("Command doesn't changed, so skip it.")
            self.logger.info("Running multiqc plugin (%s) successfully"
                             "Output in %s.\n" % (self.plugin_name, plugin.access_url))
            return plugin.access_url

    def bokeh(self):
        pass

    def plotly(self):
        pass

    def update_context(self, **kwargs):
        new_context = {}
        for key, value in kwargs.items():
            new_value = self.get_real_path(key)
            if new_value != '':
                new_context[key] = new_value
            else:
                new_context[key] = value
        self.logger.debug("Old context: %s, new context: %s" % (kwargs, new_context))
        return new_context

    def server(self):
        if self.is_server:
            if self.plugin_dir:
                src_code_dir = os.path.join(self.plugin_dir, self.plugin_name)
                process = Process(command_dir=src_code_dir, workdir=self.tmp_plugin_dir)
                port = find_free_port()
                updated_context = self.update_context(**self.context)
                process_id = process.run_command(domain=self.domain, port=port, **updated_context)
                access_url = '{protocol}://{domain}:{port}'.format(protocol=self.protocol,
                                                                   domain=self.domain,
                                                                   port=port)
                return process_id, access_url, process.workdir
            else:
                return None, None, None

    def _md5(self, string):
        md5 = hashlib.md5()
        md5.update(string.encode(encoding='utf-8'))
        return md5.hexdigest()

    def _get_args(self, **kwargs):
        sorted_kwargs = collections.OrderedDict(sorted(kwargs.items()))
        return ', '.join('%s=%r' % x for x in sorted_kwargs.items())

    def _launch_server_plugin(self):
        # write metadata to plugin.db
        metadata = {}
        metadata['name'] = self.plugin_name
        metadata['command'] = '@{}({})'.format(self.plugin_name, self._get_args(**self.context))
        metadata['command_md5'] = self._md5(metadata['command'])

        plugin = get_plugin(metadata['command_md5'], self.plugin_db)
        if not plugin:
            metadata['is_server'] = self.is_server
            process_id, access_url, workdir = self.server()
            metadata['process_id'] = process_id
            metadata['access_url'] = access_url
            metadata['workdir'] = workdir

            if access_url:
                add_plugin(**metadata, plugin_db=self.plugin_db)
            self.logger.info("Launching plugin server(%s) successfully, Serving on %s.\n" % (self.plugin_name, access_url))
            return access_url, workdir
        else:
            self.logger.info("Command doesn't changed, so skip it.")
            self.logger.info("Launching plugin server(%s) successfully, "
                             "Serving on %s.\n" % (self.plugin_name, plugin.access_url))
            return plugin.access_url, plugin.workdir

    def index_js_lst(self, js_lst):
        javascript = self._get_index_lst(js_lst, 'js')
        net_path_lst = []
        # TODO: async加速?
        for item in javascript:
            self.set_index(item.get('key'), item.get('value'), item.get('type'))
            self.logger.debug('index_db: %s, context: %s' % (self._index_db, self.context))
            net_path_lst.append(self.get_net_path(item.get('key')))
        return net_path_lst

    def autogen_js(self, required_js_lst, func_name, *args, div_id=None,
                   configs=None, html_components=None, position='prev'):
        """
        Plugin Helper: Auto generate javascript code by function arguments.
        """
        import json

        if div_id is None:
            div_id = 'plugin_' + get_candidate_name()

        if html_components:
            html_components_previous = ''
            html_components_inner = ''
            html_components_next = ''

            if position == 'prev':
                html_components_previous = html_components
            elif position == 'inner':
                html_components_inner = html_components
            elif position == 'next':
                html_components_next = html_components
            else:
                html_components_previous = html_components

            div_component = '''{html_components_previous}<div id="{div_id}"
 class="{plugin_name} biovis-plot-container">{html_components_inner}</div>
 {html_components_next}'''.format(html_components_previous=html_components_previous,
                                  div_id=div_id, plugin_name=self.plugin_name,
                                  html_components_inner=html_components_inner,
                                  html_components_next=html_components_next)
        else:
            div_component = '<div id="%s" class="%s biovis-plot-container">Loading...</div>'\
                            % (div_id, self.plugin_name)

        # Get network path
        net_path_lst = self.index_js_lst(required_js_lst)

        # Javascript function specification: the first two of js function must be div_id and configs.
        args = list(args)
        if args:
            args.insert(0, div_id)
            args.insert(1, configs)
            func_args = json.dumps(args)
        else:
            func_args = json.dumps([div_id, configs, ])

        js_code = '<script>var loader = new Loader(); loader.require(%s,  function () { window.addEventListener("load", function() { var args = JSON.parse(\'%s\'); %s.apply(this, args);})});</script>' % (net_path_lst, func_args, func_name)
        codes = [div_component, ] + [js_code, ]
        self.logger.debug("Rendered js code(%s): %s" % (self.plugin_name, codes))
        self.logger.info("Js fucntion's arguments(%s): %s" % (func_name, func_args))
        return codes

    def _transform(self, bokeh_plot=None, plotly_plot=None):
        """
        The second stage: It's necessary for some plugins to transform data or render plugin template before generating javascript code. May be you want to reimplement transform method when you have a new plugin that is not a plotly or bokeh plugin. If the plugin is a plotly or bokeh plugin, you need to reimplement plotly method or bokeh method, not transform method. (transform, save and index transformed data file.)

        :return: the path of transformed file.
        """
        def index_files(filename_lst):
            file_lst = [os.path.join(os.path.dirname(__file__), 'static', 'bokeh', filename)
                        for filename in filename_lst]
            js = self._get_index_lst(file_lst, 'js')
            # TODO: async加速?
            js_lst = []
            for item in js:
                self.set_index(item.get('key'), item.get('value'), item.get('type'))
                js_lst.append(self.get_net_path(item.get('key')))
            return js_lst

        # Only support bokeh in the current version.
        from bokeh.plotting.figure import Figure as bokehFigure
        from plotly.graph_objs import Figure as plotlyFigure
        if isinstance(bokeh_plot, bokehFigure):
            from bokeh.resources import CDN
            from bokeh.embed import autoload_static

            # Temporary directory
            dest_dir = self._get_dest_dir('js')
            plot_js_path = os.path.join(dest_dir, 'bokeh.js')

            # TODO: How to cache bokeh js?
            # js_files = ['bokeh-1.0.4.min.js', 'bokeh-gl-1.0.4.min.js', 'bokeh-tables-1.0.4.min.js',
            #             'bokeh-widgets-1.0.4.min.js']
            # js_resources = index_files(js_files)

            # URL
            virtual_path = self._get_virtual_path(plot_js_path)
            plot_js, js_tag = autoload_static(bokeh_plot, CDN, virtual_path)

            self.logger.debug('Bokeh js tag: %s' % js_tag)
            with open(plot_js_path, 'w') as f:
                f.write(plot_js)
                self.set_index('bokeh_js', plot_js_path, ftype='js')
                net_path = self.get_net_path('bokeh_js')

                self.logger.debug('index_db: %s, net_path: %s, virtual_path: %s' %
                                  (self._index_db, net_path, virtual_path))
                if net_path == virtual_path:
                    return [js_tag, ]
                else:
                    raise Exception('virtual_path(%s) and net_path(%s) are wrong.' % (virtual_path, net_path))
        elif isinstance(plotly_plot, plotlyFigure):
            from plotly.offline import plot, get_plotlyjs
            # Temporary directory
            dest_dir = self._get_dest_dir('js')
            plot_js_path = os.path.join(dest_dir, 'bokeh.js')
            plotly_js = get_plotlyjs()

            with open(plot_js_path, 'w') as f:
                f.write(plotly_js)
                self.set_index('plotly_js', plot_js_path, ftype='js')
                net_path = self.get_net_path('plotly_js')
                js_code = '<script type="text/javascript" src="%s"></script>' % net_path

                self.logger.debug('Plotlyjs: %s' % js_code)
                plot_div = plot(plotly_plot, output_type='div', include_plotlyjs=False)
                self.logger.debug('Plotly Object Js Code: %s' % js_code)
                return [js_code, plot_div, ]

    def render(self, **kwargs):
        """
        The third stage: rendering javascript snippet. The js code will inject into markdown file, and then build as html file.

        :param kwargs: all plugin args.
        :return: a list that contains js code.
        """
        pass

    def get_error_log(self, msg=None, logfile=None, msg_type='danger'):
        error_type = {
            'danger': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }

        def render_code(msg):
            code = """\
<div class='alert {}' role='alert'>
<pre class='highlight'><code>
{}
</pre></code>
</div>""".format(error_type.get(msg_type.lower(), 'alert-warning'), msg)
            return code

        if msg:
            code = render_code(msg)
        elif logfile and os.path.isfile(logfile):
            with open(logfile, 'r') as f:
                err_msg = f.read()
                code = render_code(err_msg)
        else:
            msg = 'Unknown error: for more information, please contact app developer.'
            code = render_code(msg)

        return [code, ]

    def _gen_iframe(self, rendered_lst):
        """
        Render html template as a iframe.
        """
        import tempfile
        templ_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'templates/plugin')
        templ_file = 'index.html'
        plugin = {
            "content": ''.join(rendered_lst)
        }
        self.logger.debug('Get template files from %s' % templ_dir)
        html_content = self._render_html(templ_dir, templ_file, plugin=plugin,
                                         exclude_pattern=r'.*index\.html',
                                         cache=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        # Fix bug: TypeError: a bytes-like object is required, not 'str'
        temp_file.write(html_content.encode())
        temp_file.close()

        # Don't worry it will be conflict with the same plugin in same page.
        key = self.plugin_name
        self.set_index(key, temp_file.name, ftype='html')
        iframe_tag = '<iframe src="{}" seamless frameborder="0" \
                      scrolling="no" class="iframe" \
                      name="{}" width="100%"></iframe>'
        iframe = iframe_tag.format(self.get_net_path(key), self.plugin_name)
        return iframe

    def _wrapper_render(self):
        """
        Unpack context into keyword arguments of render method.
        """
        bokeh_plot = self.bokeh()
        plotly_plot = self.plotly()  # noqa
        if bokeh_plot or plotly_plot:
            rendered_lst = self._transform(bokeh_plot=bokeh_plot, plotly_plot=plotly_plot)
            rendered_lst = self._rendered_js + rendered_lst
            if not isinstance(rendered_lst, list):
                raise NotImplementedError('Plugin does not yet support plotly framework.')

            if self.enable_iframe:
                iframe = self._gen_iframe(rendered_lst)
                rendered_lst = [iframe, ]

        elif self.is_server:
            access_url, workdir = self._launch_server_plugin()

            if workdir:
                logfile = os.path.join(workdir, 'log')
            else:
                logfile = ''

            try:
                response = requests_retry_session(
                    delay=self.wait_server_seconds,
                    backoff_factor=self.backoff_factor
                ).get(access_url, timeout=10)
            except Exception as err:
                self.logger.debug('Try to launch plugin server: %s' % str(err))
                rendered_lst = self.get_error_log(logfile=logfile)
            else:
                if response.status_code == 200:
                    iframe_tag = '<iframe src="{}" seamless frameborder="0" \
                                  scrolling="no" class="iframe" \
                                  name="{}" width="100%"></iframe>'
                    iframe = iframe_tag.format(access_url, self.plugin_name)
                    rendered_lst = [iframe, ]
                else:
                    rendered_lst = self.get_error_log(logfile=logfile)
        else:
            rendered_lst = self.render(**self._context)
            rendered_lst = self._rendered_js + rendered_lst
            if not isinstance(rendered_lst, list):
                raise NotImplementedError('You need to implement render method.')

            if self.enable_iframe:
                iframe = self._gen_iframe(rendered_lst)
                rendered_lst = [iframe, ]

        self.logger.debug('Plugin %s inject js code: %s' %
                          (self.plugin_name, rendered_lst))
        return rendered_lst

    def run(self):
        """
        Run three stages step by step.
        """
        self.prepare()
        code_lst = self._wrapper_render()
        return code_lst

    def _get_virtual_path(self, path):
        virtual_path = path.replace(self.tmp_plugin_dir, '')
        # May be the prefix is net_dir not tmp_plugin_dir
        # When the user call self.get_net_path, the prefix of the path will be self.net_dir
        # So need to add this code.
        virtual_path = virtual_path.replace(self.net_dir, '').strip('/')
        self.logger.debug('Raw path: %s, virtual_path: %s' %
                          (path, virtual_path))
        self.logger.debug('tmp_plugin_dir: %s, net_dir: %s' %
                          (self.tmp_plugin_dir, self.net_dir))

        return virtual_path

    def get_net_path(self, key, prefix='/'):
        """
        Get virtual network path for mkdocs server.
        1. Copy files from temp directory to net directory.
        2. Generate network path.

        Some files can't be copied to network directory, If developer don't call get_net_path in the plugin.
        So need to copy all needed files from temp directory to network directory manually.
        e.g. images, fonts
        """
        record_idx = self.get_index(key)
        if record_idx >= 0:
            file_path = self.get_value_by_idx(record_idx)
            virtual_path = self._get_virtual_path(file_path)
            if self.net_dir:
                # Fix bug: virtual_path will break os.path.join when it start with '/'
                self.logger.debug("virtual_path: %s" % virtual_path)
                dest_path = os.path.join(self.net_dir, virtual_path)
                self.logger.debug("dest_path: %s" % dest_path)
                check_dir(os.path.dirname(dest_path), skip=True, force=True)
                copy_and_overwrite(file_path, dest_path, is_file=True, force_remove=False)
                self.set_value_by_idx(record_idx, dest_path)
                return os.path.join(prefix, virtual_path)
            else:
                # TODO: upload to qiniu and return a url.
                return os.path.join(prefix, virtual_path)
        else:
            self.logger.warning('No such key in index db: %s' % key)

    def get_real_path(self, key):
        """
        Get real path in local file system.
        """
        record_idx = self.get_index(key)
        if record_idx > -1:
            real_file_path = self.get_value_by_idx(record_idx)
            return real_file_path
        else:
            return ''


def get_internal_plugins():
    from biovis_media_extension.plugins import internal_plugins
    return internal_plugins


def get_plugins():
    """
    Return a dict of all installed Plugins by name.
    """
    plugins = pkg_resources.iter_entry_points(group='biovis.plugins')

    return dict((plugin.name, plugin) for plugin in plugins)
