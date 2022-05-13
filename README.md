> Author: Jingcheng Yang
>
> Email: yjcyxky@163.com
>
> Date: 2018-12-13

# Biovis-report for Scientifically Interactive Report

## Introduction

Biovis-report is a fast, simple and downright gorgeous interactive report generator that's geared towards building scientific report. Report source files are written in Markdown, and configured with a single TOML configuration file.

## Dependencies

BioVis requires Python 3+ to be loaded in your environment in order for full functionality to work.

## Installation

```
# It is recommended to install Python 3.8, and don't forget to specify the biovis-report and conda-forge channels please.
conda create -c biovis-report -c conda-forge -n biovis-report python=3.8 biovis-report biovis-media-extension

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
### Base Plugins

1. boxplot-r: Interactive boxplot visualization from a Shiny app(r version).
2. corrplot-r: Interactive correlation plot visualization from a Shiny app(r version).
3. data-table-js: Another interactive data table. It is based on datatables js library.
4. density-plot: Interactive density plot visualization from a Shiny app(r version).
5. group-boxplot: Interactive group-boxplot visualization from a Shiny app(r version).
6. heatmap-d3
7. heatmap-r
8. multiqc
9. pivot-table-js: Interactive pivot-table and pivot-chart. It is based on webdatarocks and highcharts.
10. rocket-plot-r: Interactive rocket plot visualization from a Shiny app(r version).
11. scatter-plot
12. stack-barplot-r: Interactive stack barplot visualization from a Shiny app(r version).
13. tabulator: Interactive table. It is based on js library tabulator.
14. upset-r: Interactive upset plot visualization from a Shiny app(r version).
15. violin-plot-r: Interactive violin plot visualization from a Shiny app(r version).

  ```bash
  conda install -c biovis-report -c conda-forge biovis-base-plugins
  ```

### More Plugins
1. [barplot-r](https://github.com/biovis-report/barplot-r): Interactive bar plot visualization from a Shiny app(r version).

  ```bash
  conda install -c biovis-report -c conda-forge barplot-r
  ```

2. [lineplot-r](https://github.com/biovis-report/lineplot-r): Interactive line plot visualization from a Shiny app(r version).

  ```bash
  conda install -c biovis-report -c conda-forge lineplot-r
  ```

3. [lollipop-plot-r](https://github.com/biovis-report/lollipop-plot-r): Interactive lollipop plot visualization from a Shiny app(r version).

  ```bash
  conda install -c biovis-report -c conda-forge lollipop-plot-r
  ```

4. [pie-chart-js](https://github.com/biovis-report/pie-chart-js): Interactive pie chart. It is based on echarts.

  ```bash
  conda install -c biovis-report -c conda-forge pie-chart-js
  ```

### TODO
