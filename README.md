> Author: Jingcheng Yang
>
> Email: yjcyxky@163.com
>
> Date: 2018-12-13

# Biovis-report for Scientifically Interactive Report

## Introduction

Biovis-report is a fast, simple and downright gorgeous interactive report generator that's geared towards building scientific report. Report source files are written in Markdown, and configured with a single TOML configuration file.

## Dependencies

BioVis requires Python 3.7+ to be loaded in your environment in order for full functionality to work.

## Installation

```
# It is recommended to install Python>=3.7, and don't forget to specify the biovis-report and conda-forge channels please.
conda create -c biovis-report -c conda-forge -n biovis-report biovis-report biovis-media-extension

# If you want to use a plugin, just need to install it as below.
conda install -c biovis-report -c conda-forge plugin_name

# Activate bash auto-complete
activate-global-python-argcomplete
eval "$(register-python-argcomplete biovis-report)"
```

## Example

You can clone [the example repo](https://github.com/biovis-report/biovis-report-example) to taste the biovis-report.

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
### R Based Plugins

### Python Based Plugins

### JavaScript Based Plugins

## TODO
