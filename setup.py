#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
import re
import os
import sys
from biovis_report.version import get_version


long_description = (
    "Biovis-report is a fast, simple and downright gorgeous interactive report generator "
    "that's geared towards building scientific report. Report source files are written in "
    "Markdown, and configured with a single TOML configuration file."
)

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
    version=get_version(),
    url="https://github.com/biovis-report/biovis-report-core",
    license="AGPL",
    description="Interactive Report with Markdown.",
    long_description=long_description,
    author="Jingcheng Yang",
    author_email="yjcyxky@163.com",  # SEE NOTE BELOW (*)
    packages=get_packages("biovis_media_extension") + get_packages("biovis_report"),
    include_package_data=True,
    extras_require={
        'dev': [
            "pytest",
            "mkdocs",
            "mkdocs-git-revision-date-plugin",
            "mkdocs-material",
            "autopep8"
        ]
    },
    install_requires=[
        "Jinja2~=2.11",
        "PyYAML~=6.0",
        "toml~=0.10",
        "verboselogs~=1.7",
        "psutil~=5.9",
        "coloredlogs~=15.0",
        "argcomplete~=2.0",
        "jsonschema~=4.5",
        "pyparsing~=3.0",
        "plotly~=5.8",
        "requests~=2.27",
        "bokeh~=2.4",
        "Markdown~=3.3",
        "sqlalchemy~=1.4",
        "multiqc~=1.10",
        "mkdocs~=1.2",
    ],
    python_requires="!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    entry_points={
        "console_scripts": [
            "biovis-report = biovis_report.__main__:main",
        ],
        'markdown.extensions': [
            'biovis_media_extension = biovis_media_extension.extension:BioVisPluginExtension'
        ],
        'mkdocs.themes': [
            'biovis_report = biovis_report.themes.biovis_mkdocs'
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Documentation",
        "Topic :: Text Processing",
    ],
    zip_safe=False,
)
