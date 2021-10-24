# coding: utf-8
"""
Report management module:
1. Building report contains four stages: context stage, preprocessor stage, renderer stage, and report stage.
2. Context will get all environment variables in context stage, these variables will be used for remaining stages.
3. Renderer will render mkdocs config file.
4. Report will call mkdocs to build markdown files as html files. mkdocs will run a series of plugins, such as plot plugins, format conversion plugins, and evaluation plugins, to parse new markdown syntax. and then build markdown files.

Plot plugin for generate dynamic interactive plot or static image.
Format conversion plugin for converting one format to another.
Evaluation plugin for get value from the expression.
"""
from __future__ import unicode_literals

import logging
import re
import os
import sys
import yaml
import verboselogs
from os.path import join as join_path
from jinja2 import Environment, FileSystemLoader
import biovis_report.exit_code as exit_code
from biovis_report.utils import get_copyright, get_resource_dir, copy_and_overwrite

logging.setLoggerClass(verboselogs.VerboseLogger)
logger = logging.getLogger(__name__)

# Any app report MUST have these template files.
BASED_TEMPLATE_FILES = [
    "index.md",
]

META_TEMPLATE_FILE = "sample.md"


def filter_meta_templ_file(templ_files):
    pattern = r".*%s" % META_TEMPLATE_FILE
    new_templ_files = [file for file in templ_files
                       if not re.match(pattern, file)]
    return new_templ_files


def find_extra_templ_files(template_dir):
    template_files = []
    for root, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            if re.match(r".*.(md|markdown)$", filename):
                file_path = join_path(root, filename)
                # Muse be no prefix in template file path
                template = file_path.replace(template_dir, "").strip("/")
                template_files.append(template)
    diff_sets = list(set(template_files) - set(BASED_TEMPLATE_FILES))
    return diff_sets


class ReportTheme:
    def __init__(self):
        pass

    @classmethod
    def get_theme_lst(cls):
        from mkdocs.utils import get_theme_names

        # theme_lst = ("mkdocs", "readthedocs", "material", "cinder", "white_ppt")
        theme_lst = get_theme_names('biovis-report')
        return theme_lst

    @classmethod
    def get_ppt_theme_lst(cls):
        theme_lst = ("white_ppt", )
        return theme_lst

    @classmethod
    def get_html_theme_lst(cls):
        theme_lst = list(set(cls.get_theme_lst()) - set(cls.get_ppt_theme_lst()))
        return theme_lst


class Context:
    """
    The context class maintain a context database that store metadata related with project and provide a set of manipulation functions.
    """

    def __init__(self, report_dir, project_dir, editable=True,
                 enable_media_extension=True):
        self.logger = logging.getLogger("biovis-report.report_mgmt.Context")

        self.report_dir = os.path.abspath(report_dir)
        self.project_dir = os.path.abspath(project_dir)

        self._context = {
            # For Mkdocs
            "enable_media_extension": enable_media_extension,
            "editable": editable,
            "project_dir": self.project_dir,
            "docs_dir": self.report_dir,
            "html_dir": "report_html",
            "plugin_dir": join_path(self.project_dir, "report_html"),
            "project_name": os.path.basename(self.project_dir),
            "extra_header_js_lst": [
                # For non iframe mode.
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-22-load-script-0.1.3.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-22-web-inject.min.js"
            ],
            "extra_css_lst": [
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-jquery-confirm.min.css",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-loading.css",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-24-biovis-custom.css"
            ],
            "extra_js_lst": [
                # For main page.
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-jquery-2.1.1.min.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-jquery-confirm.min.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-loading.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-notify.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-stackedit-lib.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-stackedit.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-02-27-iframeResizer.min.js",
                "http://nordata-cdn.oss-cn-shanghai.aliyuncs.com/biovis-report/2019-03-21-biovis-custom.js"
            ],
            "report_menu": [
                {
                    "key": "Home",
                    "value": "index.md"
                }
            ]
        }

        self.plugin_context = {
            "wait_server_seconds": 5,
            "backoff_factor": 3,
            "protocol": "http",
            "domain": "127.0.0.1",
            "enable_iframe": True,
            "target_fsize": 10,
        }

        self.report_context = {
            "repo_url": "http://biovis.3steps.cn",
            "site_description": "BioVis is a painless reproducibility manager.",
            "site_author": "biovis",
            "copyright": get_copyright(),
            "site_name": "BioVis Report",
            "theme_name": "mkdocs",
            "menu_order": "asc",  # asc or desc
        }

        defaults = os.path.join(self.report_dir, 'defaults')
        defaults_templ = os.path.join(get_resource_dir(), 'defaults.template')
        if not os.path.isfile(defaults):
            copy_and_overwrite(defaults_templ, defaults, is_file=True)

        config = self._init_config()
        self._update_plugin_context(config)
        self._update_report_context(config)
        self.logger.debug("Initializing Report Context: %s\n" % str(self._context))

        self.set_menu(self.report_dir)
        self.logger.debug("Menu: %s" % self._context["report_menu"])
        self.optimize_menu()
        self.logger.verbose("Optimized Menu: %s\n" % self._context["report_menu"])
        # Set extra attributes from defaults file, such as copyright, site_name
        self.set_extra_context(**self.report_context)

    @property
    def context(self):
        """
        Return the context's value.
        """
        return self._context

    def set_theme_name(self, theme_name):
        if isinstance(theme_name, str):
            self._context.update({
                "theme_name": theme_name
            })

    def set_repo_url(self, repo_url):
        if repo_url:
            self._context["repo_url"] = repo_url

    def set_site_name(self, site_name):
        if site_name:
            self._context["site_name"] = site_name

    def set_site_description(self, site_description):
        if site_description:
            self._context["site_description"] = site_description

    def set_site_author(self, site_author):
        if site_author:
            self._context["site_author"] = site_author

    def set_copyright(self, copyright):
        if copyright:
            self._context["copyright"] = copyright

    def set_extra_css_lst(self, extra_css_lst):
        if len(extra_css_lst) > 0:
            self._context["extra_css_lst"].extend(extra_css_lst)

    def set_extra_js_lst(self, extra_js_lst):
        if len(extra_js_lst) > 0:
            self._context["extra_js_lst"].extend(extra_js_lst)

    def set_menu(self, report_dir, strip_pattern=""):
        """
        Add extra menu item.
        """
        # Allowed user to add more markdown files except that defined in BASED_TEMPLATE_FILES
        extra_files = filter_meta_templ_file(find_extra_templ_files(report_dir))
        extra_files = sorted(extra_files, key=str.lower, reverse=True)

        self.logger.verbose("Extra markdown files: %s\n" % extra_files)

        # More information: https://stackoverflow.com/questions/1394475/python-combine-sort-key-functions-itemgetter-and-str-lower
        def combiner(itemkey, methodname, *a, **k):
            def keyextractor(container):
                item = container[itemkey]
                method = getattr(item, methodname)
                return method(*a, **k)
            return keyextractor

        def get_basename(filename):
            m = re.search(r"(.*).(md|markdown|Md|Markdown)$", filename)
            # All files must be match the regex pattern.
            assert m is not None
            basename = m.group(1).title()
            return basename

        for item in extra_files:
            # Use the name of the first level directory as key
            keyname = item.strip("/").split("/")[0]
            # Get file name as key when it is a single file
            if re.match(r".*.(md|markdown|Md|Markdown)$", keyname):
                key = get_basename(keyname)
            else:
                key = keyname.title()

            basename = get_basename(os.path.basename(item))

            file_path = item.replace(strip_pattern, "").strip("/")
            index = next((index for (index, d) in enumerate(self._context["report_menu"])
                          if d["key"] == key), None)
            if index is not None:
                project_menu = {
                    "key": basename,
                    "value": file_path
                }
                self._context["report_menu"][index]["value"].append(project_menu)

                if self.report_context.get('menu_order').lower() == 'asc':
                    sorted_value_lst = sorted(self._context["report_menu"][index]["value"],
                                              key=combiner("key", "lower"), reverse=False)
                else:
                    sorted_value_lst = sorted(self._context["report_menu"][index]["value"],
                                              key=combiner("key", "lower"), reverse=True)

                self._context["report_menu"][index]["value"] = sorted_value_lst
            else:
                menu = {
                    "key": key,
                    "value": [
                        {
                            "key": basename,
                            "value": file_path
                        }
                    ]
                }
                if key == "About":
                    # The about must be the last one.
                    self._context["report_menu"].insert(len(self._context["report_menu"]), menu)
                else:
                    # Other menus must be between Home and About.
                    # The keys are sorted with reverse, so we can insert into 1 position.
                    self._context["report_menu"].insert(1, menu)

    def optimize_menu(self):
        for idx, menu in enumerate(self._context["report_menu"]):
            if isinstance(menu.get("value"), list) and len(menu.get("value")) == 1:
                submenu = menu.get("value")[0].get("value")
                self._context["report_menu"][idx]["value"] = submenu

    def _init_config(self):
        from biovis_report.config import init_config, get_global_config
        defaults = os.path.join(self.report_dir, 'defaults')
        if not os.path.isfile(defaults):
            defaults = os.path.join(get_resource_dir(), 'defaults.template')

        self.logger.debug("defaults file path: %s" % defaults)

        init_config(defaults)
        config = get_global_config()
        return config

    def _update_plugin_context(self, config):
        plugin = config.get_section('plugin', is_dict=True)

        for item in self.plugin_context.keys():
            self.plugin_context[item] = plugin.get(item)

        self._context.update(self.plugin_context)

    def _update_report_context(self, config):
        report = config.get_section('report', is_dict=True)

        for item in self.report_context.keys():
            self.report_context[item] = report.get(item)

        self._context.update(self.report_context)

    def set_extra_context(self, extra_css_lst=[], extra_js_lst=[], **kwargs):
        for key in kwargs.keys():
            method = 'set_%s' % key
            if hasattr(self, method) and kwargs.get(key):
                getattr(self, method)(kwargs.get(key))

        self.set_extra_css_lst(extra_css_lst)
        self.set_extra_js_lst(extra_js_lst)
        self.logger.debug("Report Context(extra context medata): %s" % str(self._context))


class Renderer:
    """
    Report renderer class that generating a mkdocs.yaml.
    """

    def __init__(self, dest_dir, ctx_instance, resource_dir=get_resource_dir()):
        self.dest_dir = dest_dir
        self.resource_dir = resource_dir
        self.context_dict = ctx_instance.context
        self.logger = logging.getLogger("biovis-report.report_mgmt.Renderer")

    def render(self):
        self._gen_docs_config()

    def _gen_docs_config(self):
        """
        Generate mkdocs.yml
        """
        mkdocs_templ = join_path(self.resource_dir, "mkdocs.yml.template")
        output_file = join_path(self.dest_dir, ".mkdocs.yml")
        self.logger.debug("Mkdocs config template: %s" % mkdocs_templ)
        self.logger.verbose("Generate mkdocs config: %s" % output_file)

        env = Environment(loader=FileSystemLoader(self.resource_dir))
        template = env.get_template("mkdocs.yml.template")
        with open(output_file, "w") as f:
            f.write(template.render(context=self.context_dict))


class Report:
    def __init__(self, project_dir):
        self.project_dir = project_dir

        # The directory where the output HTML and other files are created.
        # This can either be a relative directory, in which case it is resolved
        # relative to the directory containing your configuration file,
        # or it can be an absolute directory path from the root of your local file system.
        self.site_dir = os.path.abspath(join_path(self.project_dir, "report_html"))

        # ${project_dir}/.mkdocs.yml
        self.config_file = join_path(self.project_dir, ".mkdocs.yml")
        self.config = None

        self.logger = logging.getLogger("biovis-report.report_mgmt.Report")
        self._get_raw_config()

    def _check_config(self, msg, load_config=True):
        from mkdocs import config as mkdocs_config

        if os.path.isfile(self.config_file):
            if load_config:
                self.config = mkdocs_config.load_config(config_file=self.config_file,
                                                        site_dir=self.site_dir)
        else:
            raise Exception(msg)

    def _get_raw_config(self):
        with open(self.config_file) as f:
            self.raw_config = yaml.load(f, Loader=yaml.FullLoader)

    def update_config(self, key, value, append=False):
        """
        Update mkdocs config.
        """
        if append:
            # It will be failed when the value is None.
            # e.g. extra_css or extra_javascript
            if isinstance(self.raw_config.get(key), list):
                self.raw_config.get(key).append(value)
        else:
            self.raw_config.update({
                key: value
            })

    def save_config(self):
        with open(self.config_file, "w") as f:
            f.write(self.raw_config)

    def build(self, templ_type="html"):
        from mkdocs.commands.build import build as build_docs

        self._check_config("Attempting to build docs but the mkdocs.yml doesn't exist."
                           " You need to call render/new firstly.")
        build_docs(self.config, live_server=False, dirty=False,
                   templ_type=templ_type)

    def server(self, dev_addr=None, livereload="livereload", templ_type="html"):
        from mkdocs.commands.serve import dev_serve as serve_docs

        self._check_config("Attempting to serve docs but the mkdocs.yml doesn't exist."
                           " You need to call render/new firstly.", load_config=False)
        serve_docs(config_file=self.config_file, dev_addr=dev_addr,
                   livereload=livereload, site_dir=self.site_dir,
                   templ_type=templ_type)


def build(report_dir, project_dir, resource_dir=get_resource_dir(), repo_url=None,
          site_description=None, site_author=None, copyright=None,
          site_name=None, dev_addr=None, theme_name=None,
          mode="build", force=False, editable=True,
          enable_media_extension=True):
    """
    Build an app report.

    :param: report_dir: a directory for report templates
    :param: project_dir: a project output directory.
    :param: resource_dir: a directory that host template files.
    :param: repo_url: a repo url and its prefix is "http://biovis.3steps.cn/".
    :param: site_decription:
    :param: site_author:
    :param: copyright:
    :param: site_name: it will show as website logo.
    :param: server: a cromwell server name
    :param: dev_addr:
    :param: theme_name:
    :param: mode: mkdocs be ran as which mode, build, livereload or server.
    :param: force: force to renew the mkdocs outputs.
    :param: editable: whether the report can be edited by users.
    :param: enable_media_extension: whether enable media extension.
    :return:
    """
    from biovis_report.utils import check_plugin

    if enable_media_extension:
        if not check_plugin():
            sys.exit(exit_code.INVALID_DEPS)

    # Context: generate context metadata.
    logger.info("\n1. Generate report context.")
    ctx_instance = Context(report_dir, project_dir, editable=editable,
                           enable_media_extension=enable_media_extension)
    ctx_instance.set_extra_context(repo_url=repo_url, site_description=site_description,
                                   site_author=site_author, copyright=copyright, site_name=site_name,
                                   theme_name=theme_name)
    logger.verbose("Context: %s" % ctx_instance.context)
    logger.success("Context: generate report context successfully.")

    # Renderer: render report config file.
    logger.info("\n2. Render report config file.")
    renderer = Renderer(project_dir, ctx_instance=ctx_instance, resource_dir=resource_dir)
    renderer.render()
    logger.success("Render config file successfully.")

    # Report: build markdown files to html.
    if theme_name in ReportTheme.get_ppt_theme_lst():
        templ_type = "ppt"
    elif theme_name in ReportTheme.get_html_theme_lst():
        templ_type = "html"
    else:
        templ_type = "html"

    report = Report(project_dir)
    if mode == "build":
        logger.info("\n3. Build %s by mkdocs" % report_dir)
        report.build(templ_type=templ_type)
        site_dir = join_path(project_dir, "report_html")
        logger.success("Build markdown files successfully. "
                       "(Files in %s)" % site_dir)
    elif mode == "livereload":
        logger.info("\n3. Serve %s in livereload mode by mkdocs" % report_dir)
        report.server(dev_addr=dev_addr, livereload="livereload",
                      templ_type=templ_type)
    elif mode == "server":
        logger.info("\n3. Serve %s by mkdocs" % report_dir)
        report.server(dev_addr=dev_addr, livereload="no-livereload",
                      templ_type=templ_type)


def get_mode():
    return ["build", "server", "livereload"]
