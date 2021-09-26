> Author: Jingcheng Yang
>
> Email: yjcyxky@163.com
>
> Date: 2018-12-13

# Biovis-report for Scientifically Interactive Report

[中文文档](http://docs.3steps.cn)

## Introduction

Biovis-report is a fast, simple and downright gorgeous interactive report generator that's geared towards building scientific report. Report source files are written in Markdown, and configured with a single TOML configuration file.

## Dependencies

BioVis requires Python 3+ to be loaded in your environment in order for full functionality to work.

## Installation

```
virtualenv .env
source .env/bin/activate
pip install biovis-report

# If you want to use a plugin, just need to install it as below.
conda install plugin_name

# Activate bash auto-complete
activate-global-python-argcomplete
eval "$(register-python-argcomplete biovis-report)"
```

## Usage

Below is biovis-report's basic help text. Biovis-report expects one of three usage modes to
be indicated as it's first argument: report, manplugin, or plugins.

```
usage: biovis-report <positional argument> [<args>]

Description: A tool for generating a scientifically interactive report.

positional arguments:
  {report, manplugin, plugins}

optional arguments:
  -h, --help            show this help message and exit
```

## Plugins
1. [boxplot-r: Interactive boxplot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/boxplot-r.html)
2. [corrplot-r: Interactive correlation plot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/corrplot-r.html)
3. [data-table-js: Another interactive data table. It is based on datatables js library.](http://docs.3steps.cn/docs/plugins/data-table-js.html)
4. [density-plot: Interactive density plot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/density-plot.html)
5. [group-boxplot: Interactive group-boxplot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/group-boxplot.html)
6. [pivot-table-js: Interactive pivot-table and pivot-chart. It is based on webdatarocks and highcharts.](http://docs.3steps.cn/docs/plugins/pivot-table-js.html)
7. [rocket-plot-r: Interactive rocket plot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/rocket-plot-r.html)
8. [stack-barplot-r: Interactive stack barplot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/stack-barplot-r.html)
9. [upset-r: Interactive upset plot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/upset-r.html)
10. [violin-plot-r: Interactive violin plot visualization from a Shiny app(r version).](http://docs.3steps.cn/docs/plugins/violin-plot-r.html)