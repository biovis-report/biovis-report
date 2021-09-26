#!/usr/bin/env python
# -*- coding:utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
BioVis report is a tool for generating an interactive report.
"""
from __future__ import unicode_literals, absolute_import
import argcomplete
import argparse
import os
import sys
import logging
import coloredlogs
import verboselogs
from biovis_report.version import get_version
from biovis_report.report_mgmt import (get_mode, ReportTheme)
from biovis_report.plugin_utils import (listplugins, get_plugin)
from biovis_report.utils import is_valid, is_valid_url


logging.setLoggerClass(verboselogs.VerboseLogger)
logger = logging.getLogger('biovis-report')


def set_logger(loglevel):
    if loglevel == logging.SPAM:
        fmt = '%(asctime)s - %(name)s(%(lineno)d) - %(levelname)s - %(message)s'
        coloredlogs.install(level=logging.DEBUG, fmt=fmt)
    elif loglevel == logging.DEBUG:
        fmt = '%(name)s - %(levelname)s - %(message)s'
        coloredlogs.install(level=loglevel, fmt=fmt)
    else:
        fmt = '%(message)s'
        coloredlogs.install(level=loglevel, fmt=fmt)


def call_list_plugins(args):
    plugins = listplugins()
    if plugins:
        print(sorted(plugins))
    else:
        logger.warning("No any plugins are installed.")


def call_plugin_readme(args):
    output = args.output
    format = args.format
    plugin_name = args.plugin_name
    plugin = get_plugin(plugin_name)
    if plugin:
        plugin.show_help(ftype=format, output=output)


def call_report(args):
    import atexit
    from biovis_report.report_mgmt import build as build_report
    from biovis_report.utils import Process

    process = Process()
    atexit.register(process.clean_processs)

    repo_url = args.repo_url
    site_name = args.site_name
    site_description = args.site_description
    site_author = args.site_author

    project_dir = args.project_dir
    theme = args.theme
    dev_addr = args.dev_addr
    force = args.force
    mode = args.mode

    enable_media_extension = args.enable_plugin

    report_dir = args.report_dir

    if os.path.abspath(project_dir) == os.path.abspath(report_dir):
        raise Exception("project directory(%s) should not be same with template directory(%s)"
                        % (project_dir, report_dir))

    # All are False or all are True
    editable = mode == 'livereload'

    build_report(report_dir, project_dir, repo_url=repo_url, site_description=site_description,
                 site_author=site_author, site_name=site_name, mode=mode, dev_addr=dev_addr,
                 force=force, theme_name=theme, editable=editable,
                 enable_media_extension=enable_media_extension)


def call_version(args):
    print("BioVis Report %s" % get_version())


description = """Global Management:
    version     Show the version.

Report Management:
    report      Generate a report for an app or the specified template files automatically.
    manplugin   Get manual about report plugin.
    plugins     List all plugins that is supported by biovis report.
"""


parser = argparse.ArgumentParser(
    description='Description: A tool for generating a scientifically interactive report.',
    usage='biovis <positional argument> [<args>]',
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('--handler', action='store', default='stream', choices=('stream', 'file'),
                    help="Log handler, stream or file?")
group = parser.add_mutually_exclusive_group()
group.add_argument('--debug', action='store_true', default=False, help="Debug mode.")
group.add_argument('-q', '--quite', action='store_true', default=False, help="Only display key message.")
group.add_argument('-v', '--verbose', action='count', default=0, help='Increase output verbosity')

sub = parser.add_subparsers(title='commands', description=description)
pluginlst = sub.add_parser(name="plugins",
                           description="List all plugins that is supported by biovis report.",
                           usage="biovis plugins",
                           formatter_class=argparse.ArgumentDefaultsHelpFormatter)
pluginlst.set_defaults(func=call_list_plugins)

version = sub.add_parser(name="version",
                         description="Show the version.",
                         usage="biovis version",
                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
version.set_defaults(func=call_version)

plugin = sub.add_parser(name="manplugin",
                        description="Get man about report plugin.",
                        usage="biovis manplugin <plugin_name> [<args>]",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
plugin.add_argument('plugin_name', action='store', choices=listplugins(),
                    help='The plugin name for your report.', metavar="plugin_name")
plugin.add_argument('-o', '--output', action='store', help='output file name.')
plugin.add_argument('-f', '--format', action='store', help='output format.',
                    default='browser', choices=('html', 'markdown', 'browser'))
plugin.set_defaults(func=call_plugin_readme)

report = sub.add_parser(name="report",
                        description="Generate report for your app results.",
                        usage="biovis report [<args>]",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
report.add_argument('-t', '--report-dir', action='store', type=is_valid, default=os.getcwd(),
                    help='The directory that contains your report template files.')
report.add_argument('-m', '--mode', action='store', default='livereload', choices=get_mode(), help='Which mode for your report.')
report.add_argument('--dev-addr', action='store', default='127.0.0.1:8000', help='Development server address.',
                    metavar='<IP:PORT>')
report.add_argument('-f', '--force', action='store_true', default=False, help='Force to regenerate files.')
report.add_argument('-e', '--enable-plugin', action='store_true', default=False,
                    help='Enable to support biovis plugins.')
report.add_argument('-p', '--project-dir', action='store', default=os.getcwd(),
                    help='Your project directory', type=is_valid)
report.add_argument('--theme', action='store', choices=ReportTheme.get_theme_lst(),
                    help='Theming your report by using the specified theme.')
report.add_argument('--repo-url', action='store', help='Your project repo url', type=is_valid_url)
report.add_argument('--site-name', action='store', help='The site name for your report website')
report.add_argument('--site-author', action='store', help='The site author')
report.add_argument('--site-description', action='store', help='The site description')
report.set_defaults(func=call_report)


def main():
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.debug:
        loglevel = logging.DEBUG
    elif args.verbose:
        verbose = args.verbose
        # Configure logger for requested verbosity.
        if verbose >= 3:
            loglevel = logging.SPAM
        elif verbose >= 2:
            loglevel = logging.DEBUG
        elif verbose >= 1:
            loglevel = logging.VERBOSE
    elif args.quite:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO

    set_logger(loglevel=loglevel)

    if len(sys.argv) == 1:
        print("Missing argument('%s --help' for help)" % sys.argv[0])
        print(description)
    else:
        args.func(args)


if __name__ == "__main__":
    sys.exit(main())
