#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
import re
import os
import sys
from biovis_report.version import get_version as get_report_version


long_description = (
    "Biovis-report is a fast, simple and downright gorgeous interactive report generator "
    "that's geared towards building scientific report. Report source files are written in "
    "Markdown, and configured with a single TOML configuration file."
)


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, "__init__.py")).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, "__init__.py"))]


if sys.argv[-1] == "publish":
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(get_report_version()))
    print("  git push --tags")
    sys.exit()


setup(
    name="biovis-report",
    version=get_report_version(),
    url="https://github.com/biovis-report/biovis-report-core",
    license="AGPL",
    description="Interactive Report with Markdown.",
    long_description=long_description,
    author="Jingcheng Yang",
    author_email="yjcyxky@163.com",  # SEE NOTE BELOW (*)
    packages=get_packages("mkdocs") + get_packages("biovis_report"),
    include_package_data=True,
    install_requires=[
        "click>=3.3",
        "Jinja2>=2.7.1",
        "livereload>=2.5.1",
        "lunr[languages]>=0.5.2",
        "Markdown>=2.3.1",
        "PyYAML>=3.10",
        "tornado>=5.0",
        "beautifulsoup4",
        "psutil",
        "coloredlogs",
        "argcomplete",
        "pymdown-extensions",
        "verboselogs>=1.7",
        "jsonschema>=4.1.2"
    ],
    python_requires="!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    entry_points={
        "console_scripts": [
            "biovis-report = biovis_report.__main__:main",
        ],
        "mkdocs.themes": [
            "biovis_mkdocs = mkdocs.themes.biovis_mkdocs",
            "biovis_rtd = mkdocs.themes.biovis_readthedocs",
            "white_ppt = mkdocs.themes.white_ppt",
            "mkdocs = mkdocs.themes.mkdocs",
            "docskimmer = mkdocs.themes.mkdocs_docskimmer",
        ],
        "mkdocs.plugins": [
            "search = mkdocs.contrib.search:SearchPlugin",
            "header_injector = mkdocs.contrib.header_injector:HeaderInjectorPlugin"
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Documentation",
        "Topic :: Text Processing",
    ],
    zip_safe=False,
)
