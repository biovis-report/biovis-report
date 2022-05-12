# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import re
import logging
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from biovis_media_extension.plugin import get_plugins, get_internal_plugins
from biovis_media_extension.convertor import get_convertors
from biovis_media_extension.utils import BashColors
from biovis_media_extension.exceptions import PluginSyntaxError, ValidationError
from biovis_media_extension.plugin import BasePlugin
from biovis_media_extension.convertor import BaseConvertor


class Code:
    """
    Parse plugin call code and execute it.
    """

    def __init__(self, code, net_dir, sync_oss=True, sync_http=True,
                 sync_ftp=True, target_fsize=10, protocol='http',
                 domain='127.0.0.1', enable_iframe=True,
                 wait_server_seconds=5, backoff_factor=3):
        """
        Initialize code instance.

        :param: code: code string, such as @plugin_name(arg1=value, arg2=value, arg3=value)
        :param: net_dir: a directory which is used as html directory. plugin and convertor maybe generate some files that are needed by html, so all these files should be copied to net directory.
        """
        self.logger = logging.getLogger(__name__)
        self._code = code
        self.installed_plugins = get_plugins()
        self.internal_plugins = get_internal_plugins()
        self.installed_convertors = get_convertors()
        self.net_dir = net_dir
        self.target_fsize = target_fsize
        self.sync_oss = sync_oss
        self.sync_http = sync_http
        self.sync_ftp = sync_ftp
        self.protocol = protocol
        self.domain = domain
        self.enable_iframe = enable_iframe
        self.wait_server_seconds = wait_server_seconds
        self.backoff_factor = backoff_factor

    def load_convertor(self, name, context):
        if name not in self.installed_convertors:
            raise ValidationError('The "{0}" convertor is not installed'.format(name))

        Convertor = self.installed_convertors[name].load()

        if not issubclass(Convertor, BaseConvertor):
            raise ValidationError('{0}.{1} must be a subclass of {2}.{3}'.format(
                                  Convertor.__module__, Convertor.__name__, BaseConvertor.__module__,
                                  BaseConvertor.__name__))

        convertor = Convertor(context, self.net_dir)
        return convertor

    def load_plugin(self, name, context):
        InternalPlugin = self.internal_plugins.get(name)
        if InternalPlugin:
            plugin = InternalPlugin(context=context, net_dir=self.net_dir, target_fsize=self.target_fsize,
                                    sync_oss=self.sync_oss, sync_http=self.sync_http,
                                    sync_ftp=self.sync_ftp, protocol=self.protocol, domain=self.domain,
                                    enable_iframe=self.enable_iframe,
                                    wait_server_seconds=self.wait_server_seconds,
                                    backoff_factor=self.backoff_factor)
        else:
            if name not in self.installed_plugins:
                raise ValidationError('The "{0}" plugin is not installed'.format(name))

            Plugin = self.installed_plugins[name].load()

            if not issubclass(Plugin, BasePlugin):
                raise ValidationError('{0}.{1} must be a subclass of {2}.{3}'.format(
                                      Plugin.__module__, Plugin.__name__, BasePlugin.__module__,
                                      BasePlugin.__name__))

            plugin = Plugin(context=context, net_dir=self.net_dir, target_fsize=self.target_fsize,
                            sync_oss=self.sync_oss, sync_http=self.sync_http,
                            sync_ftp=self.sync_ftp, protocol=self.protocol, domain=self.domain,
                            enable_iframe=self.enable_iframe,
                            wait_server_seconds=self.wait_server_seconds,
                            backoff_factor=self.backoff_factor)
        return plugin

    def _parse(self):
        """
        Parse plugin call for identify plugin name and keyword arguments.
        """
        from biovis_media_extension.syntax_parser import plugin_kwarg
        from pyparsing import ParseException

        # Split func with args
        pattern = r'^@(?P<plugin_name>[-\w]+)(?P<args_str>.*)$'
        matched = re.match(pattern, self._code)
        if matched:
            plugin_name = matched.group('plugin_name')
            args_str = matched.group('args_str')
            color_msg = BashColors.get_color_msg('SUCCESS',
                                                 '\nParsed biovis plugin command: %s and %s' %
                                                 (plugin_name, args_str))
            self.logger.info(color_msg)

            try:
                # Bug: maybe error when the argument value is a string as file name.
                # filter_ctx_files function's pattern '^(/)?([^/\0]+(/)?)+$' may treat a string as a file but it's not true.
                items = plugin_kwarg.parseString(args_str).asList()
                plugin_kwargs = {i[0]: i[1] for i in items if len(i) == 2}
            except ParseException as err:
                color_msg = BashColors.get_color_msg('DANGER',
                                                     'Biovis plugin command[plugin_name: %s, args: %s]: syntax error - %s' % (plugin_name, args_str, str(err)))
                self.logger.error(color_msg)
                raise PluginSyntaxError('Can not parse biovis plugin command.')
            self.logger.info('Plugin name: %s, Plugin kwargs: %s' % (plugin_name, str(plugin_kwargs)))
            return plugin_name, plugin_kwargs
        else:
            color_msg = BashColors.get_color_msg('WARNING', 'Can not parse biovis plugin command.')
            self.logger.error(color_msg)
            raise PluginSyntaxError('Can not parse biovis plugin command.')

    def _recursive_call(self, filepath, convertor_key_lst):
        """
        Call convertor in the chain.
        """
        if len(convertor_key_lst) == 1:
            convertor = self.load_convertor(convertor_key_lst[0])
            return convertor.run(filepath)
        else:
            convertor = self.load_convertor(convertor_key_lst[0])
            return self._recursive_call(convertor.run(filepath), convertor_key_lst[1:])

    def _convert_context(self, plugin_kwargs):
        """
        Parse convertor from biovis plugin kwargs, and then call convertor in the chain. (Get real path of all files.)
        """
        context = {}
        for key, value in plugin_kwargs.items():
            if isinstance(value, str):
                convertor_str_lst = [i.strip() for i in value.split('|')]
                if len(convertor_str_lst) == 1:
                    filepath = convertor_str_lst[0]
                else:
                    filepath = convertor_str_lst[0]
                    convertor_key_lst = convertor_str_lst[1:]
                    filepath = self._recursive_call(filepath, convertor_key_lst)
                context.update({
                    key: filepath
                })
            else:
                context.update({
                    key: value
                })
        self.logger.debug('Context: %s' % context)
        return context

    def _extract_context(self, plugin_kwargs):
        context = {}
        for key, value in plugin_kwargs.items():
            convertor_str_lst = [i.strip() for i in value.split('|')]
            # For "filepath | convertor"
            context.update({
                key: convertor_str_lst[0]
            })
        return context

    def generate(self):
        # Get all plugin kwargs and plugin name.
        plugin_name, plugin_kwargs = self._parse()
        # Run convertor and get new plugin kwargs as context.
        context = self._convert_context(plugin_kwargs)
        # e.g. ["<script id='plot' src=''>", "</script>"]
        try:
            plugin = self.load_plugin(plugin_name, context)
            code_lst = plugin.run()
        except Exception as err:
            import traceback
            kwargs_str = ', '.join('%s=%r' % x for x in plugin_kwargs.items())
            code = """\
<div class='alert {class_name}' role='alert'>
<pre><code>
Error: for more information, please check logs as follows.

{err}

Plugin:
{plugin_name}

Arguments:
{plugin_kwargs}

Context:
{context}
</code></pre>
</div>""".format(class_name='alert-danger', err=str(err),
                 plugin_name=plugin_name, plugin_kwargs=kwargs_str,
                 context=str(context))
            code_lst = [code, ]
            self.logger.debug("Generate code for %s error: %s" % (plugin_name, str(err)))
            self.logger.debug(traceback.format_exc())
            self.logger.warning("Generate code for %s error: %s" % (plugin_name, str(err)))
        return code_lst


class BioVisPluginPreprocessor(Preprocessor):
    """
    Dynamic Plot / Multimedia Preprocessor for Python-Markdown.
    """

    def __init__(self, md, config):
        super(BioVisPluginPreprocessor, self).__init__(md)
        self.logger = logging.getLogger(__name__)
        self.net_dir = config.get('net_dir', None)
        self.target_fsize = config.get('target_fsize', 10)
        self.sync_oss = config.get('sync_oss', True)
        self.sync_http = config.get('sync_http', True)
        self.sync_ftp = config.get('sync_ftp', True)
        self.protocol = config.get('protocol', 'http')
        self.domain = config.get('domain', '127.0.0.1')
        self.enable_iframe = config.get('enable_iframe', True)
        self.wait_server_seconds = config.get('wait_server_seconds', 5)
        self.backoff_factor = config.get('backoff_factor', 3)

        if self.net_dir is None:
            color_msg = BashColors.get_color_msg('WARNING', "biovis_media_extension's kwarg net_dir is not set, so it will be instead by qiniu url.")
            self.logger.warning(color_msg)

    def run(self, lines):
        new_lines = []
        block = []
        flag = False
        start_pattern = r'^@[-\w]+\(.*'
        end_pattern = r'.*\)$'
        for line in lines:
            striped_line = line.strip()
            start_matched = re.match(start_pattern, striped_line)
            end_matched = re.match(end_pattern, striped_line)
            # Single line
            if start_matched and end_matched:
                block.append(striped_line)
                code_str = re.sub(r'\s', '', ''.join(block))
                # Parse plugin call code, and then call plugin.
                code_instance = Code(code_str, self.net_dir, target_fsize=self.target_fsize,
                                     sync_oss=self.sync_oss, sync_http=self.sync_http, sync_ftp=self.sync_ftp, protocol=self.protocol, domain=self.domain,
                                     enable_iframe=self.enable_iframe,
                                     wait_server_seconds=self.wait_server_seconds,
                                     backoff_factor=self.backoff_factor)
                js_code_lines = code_instance.generate()
                new_lines.extend(js_code_lines)
                block = []
            # Multiple lines start point
            elif start_matched:
                flag = True
                block.append(striped_line)
            # Multiple lines
            elif flag:
                if end_matched:
                    block.append(striped_line)
                    code_str = re.sub(r'\s', '', ''.join(block))

                    # Parse plugin call code, and then call plugin.
                    code_instance = Code(code_str, self.net_dir)
                    js_code_lines = code_instance.generate()
                    new_lines.extend(js_code_lines)
                    block = []
                    flag = False
                else:
                    block.append(line)
            # Not matched
            else:
                new_lines.append(line)

        return new_lines


class BioVisPluginExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'net_dir': [None, 'A directory which is used as html directory.'],
            'protocol': ['http', 'Http protocol'],
            'domain': ['127.0.0.1', 'Domain for plugin server'],
            'enable_iframe': [True, 'Enable to generate iframe for all plugins'],
            'wait_server_seconds': [5, 'If you specify a wait_server_seconds that greater than 0, sleep() will sleep for wait_server_seconds. When wait_server_seconds less than or equal than 0, it will be set 0.'],
            'backoff_factor': [3, 'A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay). urllib3 will sleep for: {backoff factor} * (2 ** ({number of total retries} - 1)) seconds. If the backoff_factor is 0.1, then sleep() will sleep for [0.0s, 0.2s, 0.4s, …] between retries. It will never be longer than 120s.'],
            'target_fsize': [10, 'All files that size is less than target_fsize could be cached.']
        }

        self.config.update({
            'net_dir': [kwargs.get('net_dir'), 'a directory which is used as html directory.'],
            'protocol': [kwargs.get('protocol'), 'Http protocol'],
            'domain': [kwargs.get('domain'), 'Domain for plugin server'],
            'enable_iframe': [kwargs.get('enable_iframe'), 'Enable to generate iframe for all plugins'],
            'wait_server_seconds': [kwargs.get('wait_server_seconds'), 'If you specify a wait_server_seconds that greater than 0, sleep() will sleep for wait_server_seconds. When wait_server_seconds less than or equal than 0, it will be set 0.'],
            'backoff_factor': [kwargs.get('backoff_factor'), 'A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay). urllib3 will sleep for: {backoff factor} * (2 ** ({number of total retries} - 1)) seconds. If the backoff_factor is 0.1, then sleep() will sleep for [0.0s, 0.2s, 0.4s, …] between retries. It will never be longer than 120s.'],
            'target_fsize': [kwargs.get('target_fsize') or 10, 'All files that size is less than target_fsize could be cached.']
        })

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)

        plugin_preprocessor = BioVisPluginPreprocessor(md, self.getConfigs())
        md.preprocessors.add('plugin_preprocessor', plugin_preprocessor,
                             '<normalize_whitespace')


# http://pythonhosted.org/Markdown/extensions/api.html#makeextension
def makeExtension(*args, **kwargs):
    return BioVisPluginExtension(*args, **kwargs)
