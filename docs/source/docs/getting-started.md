## Introduction

Biovis-report is a fast, simple and downright gorgeous interactive report generator that's geared towards building scientific report.Report source files are written in Markdown and you can also integrate scientific data, plots into the report source file by using a set of biovis plugins. It is designed to be easy to use and can be extended with third-party themes, scientific visualization plugins.

Please see the <a href="/docs/plugins/" target="_blank">plugins</a> for a full plugin guide.

## Features

- Build static website from Markdown files.
- Use visualization plugins to visualize your scientific data.
- Use the built-in themes, third party themes or create your own.
- Publish your website or share the report source files to other researchers.

## Run an Example

To familiarize you with biovis-reports and how to write a report, let's reproduce a example report together (as shown in the video below).

<iframe
    width="560"
    height="315"
    src="https://www.youtube.com/embed/MZ1Kv75t_Mc"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
></iframe>

!!! note
    BioVis requires Python 3.7+, R 3.6.3+, and a set of R/Python/JavaScript packages to be loaded in your environment in order for full functionality to work. For easier to install all the depedencies, we choose the miniconda (you can also use anaconda).

### Step 1: Install miniconda

> If you have installed miniconda or anaconda, please skip the step 1.

To install miniconda, click the `Download Link` to download the miniconda package and install it.

| Platform              |              File Name               |                                          Download Link                                          |                             More Details                              |
| --------------------- | :----------------------------------: | :---------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------: |
| For MacOSX (Intel)    | Miniconda3-latest-MacOSX-x86_64.pkg  | <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg">Download</a>  |   <a href="/docs/installation/mac/#miniconda">Step by Step Guide</>   |
| For MacOSX (Apple M1) |  Miniconda3-latest-MacOSX-arm64.pkg  |  <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg">Download</a>  |   <a href="/docs/installation/mac/#miniconda">Step by Step Guide</>   |
| For Windows           | Miniconda3-latest-Windows-x86_64.exe | <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe">Download</a> | <a href="/docs/installation/windows/#miniconda">Step by Step Guide</> |
| For Linux             |  Miniconda3-latest-Linux-x86_64.sh   |  <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"> Download</a>  | <a href="https://ostechnix.com/how-to-install-miniconda-in-linux/" target="_blank">Step by Step Guide</a>  |

For more details, see the [Miniconda Guide](https://docs.conda.io/en/latest/miniconda.html).

### Step 2: Create a conda environment and intall biovis-report

Open your terminal and run the following command.

> Don't install these packages in existing conda environments (they may disturb your environment). Please use `conda create` command to create a new conda environment for the biovis-report.

```
# All related dependencies are located in the biovis-report and conda-forge channel, so you need to specify the two channels.
conda create --channel biovis-report --channel conda-forge --name biovis-report biovis-report

# After the previous command is finished, you need to activate the biovis-report environment
conda activate biovis-report
```

!!! note "Too slow?"
    Mamba is a re-implementation of the Conda package manager, designed to be: 
    
    Fast.
    
    Backwards compatible, with the same command-line options.
    
    Eventually, add more features.

    ```
    # Install mamba
    conda install mamba

    # Use mamba instead of conda, e.g.
    conda create --channel biovis-report --channel conda-forge --name biovis-report biovis-report
    # is equal to
    mamba create --channel biovis-report --channel conda-forge --name biovis-report biovis-report
    ```

### Step 3: Install a set of scientific visualization plugins

If you want to integrate the scientific charts in the report, you need to install the visualization plugins.

```
# Install all plugins
conda install --channel biovis-report --channel conda-forge biovis-rbased-plugins biovis-pybased-plugins biovis-jsbased-plugins
```

!!! note

    All plugins are divided into three plugin packages depending on the development language (`biovis-rbased-plugins`, `biovis-pybased-plugins`, `biovis-jsbased-plugins`). 

    If you want to know the difference between the plugin packages, you can read <a href="/docs/plugins/" target="_blank">the plugin guide</a>.

    If you don't care the details, you can install all the three plugin packages directlly.

### Step 4: Test your installation

Run the command `biovis-report -h`, You'll see the following output.

```
# Command
biovis-report -h

# Output
usage: biovis <positional argument> [<args>]

Description: A tool for generating a scientifically interactive report.

optional arguments:
  -h, --help            show this help message and exit
  --handler {stream,file}
                        Log handler, stream or file?
  --debug               Debug mode.
  -q, --quite           Only display key message.
  -v, --verbose         Increase output verbosity

commands:
  Global Management:
      version     Show the version.
  
  Report Management:
      report      Generate a report for an app or the specified template files automatically.
      manplugin   Get manual about report plugin.
      plugins     List all plugins that is supported by biovis report.

  {plugins,version,manplugin,report}
```

If you have installed the three plugin packages and run the command `biovis-report plugins`, you'll see the following output.

```
# Command
biovis-report plugins

# Output
['boxplot-r', 'corrplot-r', 'data-table-js', 'density-plot', 'group-boxplot', 'heatmap-d3', 'heatmap-r', 'multiqc', 'pivot-table-js', 'rocket-plot-r', 'scatter-plot', 'stack-barplot-r', 'tabulator', 'upset-r', 'violin-plot-r']
```

Everything is okay, you can write your first report. Keep going on.

### Step 5: Download the example source files

Please download <a href="https://github.com/biovis-report/biovis-report-example/archive/refs/heads/master.zip">the example archive file</a> and unzip it.

Or

If you have `git` on your machine, you can clone [the example repo](https://github.com/biovis-report/biovis-report-example) to taste the biovis-report.

```
git clone https://github.com/biovis-report/biovis-report-example
```

### Step 6: Launch the example

Locate your download and change the working directory to it. e.g. the `biovis-report-example` is located in the `/Users/codespace/Downloads/biovis-report-example`

```
cd /Users/codespace/Downloads/biovis-report-example

biovis-report report -t /Users/codespace/Downloads/biovis-report-example/example -m livereload -p /Users/codespace/Downloads/biovis-report-example --enable-plugin --theme biovis_report
```