!!! note

    1. Therefore, the current version of BioVisReport does not support Windows because we cannot make all plugins work properly on Windows. We consider to support Windows in next version. We're very sorry for the inconvenience.

    2. BioVisReport requires Python 3.7+ and a set of R/Python/JavaScript packages to be loaded in your environment in order for full functionality to work. For easier to install all the depedencies, we choose the miniconda (you can also use anaconda).

## Step 1: Install miniconda

> If you have installed miniconda or anaconda, please skip the step 1.

To install miniconda, click the `Download Link` to download the miniconda package and install it.

| Platform              |              File Name               |                                          Download Link                                          |                             More Details                              |
| --------------------- | :----------------------------------: | :---------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------: |
| For MacOSX (Intel)    | Miniconda3-latest-MacOSX-x86_64.pkg  | <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg">Download</a>  |   <a href="/docs/installation/mac/#miniconda">Step by Step Guide</>   |
| For MacOSX (Apple M1) |  Miniconda3-latest-MacOSX-arm64.pkg  |  <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg">Download</a>  |   <a href="/docs/installation/mac/#miniconda">Step by Step Guide</>   |
| For Linux             |  Miniconda3-latest-Linux-x86_64.sh   |  <a href="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"> Download</a>  | <a href="https://ostechnix.com/how-to-install-miniconda-in-linux/" target="_blank">Step by Step Guide</a>  |
<!-- | For Windows           | Miniconda3-latest-Windows-x86_64.exe | <a disabled href="https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe">Download</a> | <a disabled href="/docs/installation/windows/#miniconda">Step by Step Guide</> | -->

Please run the following command to confirm that conda has been installed successfully.

```
conda -V

# Output
conda 4.12.0
```

For more details, see the [Miniconda Guide](https://docs.conda.io/en/latest/miniconda.html).

## Step 2: Installation

### Quick Installation

To make it easier for users to install `biovis-report` quickly, we have created a conda environment file, you just need to download [this file](/assets/environment.yml) and run the following command to configure biovis-report.

```
conda env create -f environment.yml
```

After the process, an environment called "biovis-report" will be installed on your machine. The quick installation works the same as the following step-by-step installation. So you can skip the `Step by Step Installation`.

### Step by Step Installation
#### 1. Create a conda environment and intall biovis-report

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
    
    - Fast.
    
    - Backwards compatible, with the same command-line options.
    
    - Eventually, add more features.

    ```
    # Install mamba
    conda install mamba

    # Use mamba instead of conda, e.g.
    conda create --channel biovis-report --channel conda-forge --name biovis-report biovis-report
    # is equal to
    mamba create --channel biovis-report --channel conda-forge --name biovis-report biovis-report
    ```

#### 2. Install a set of scientific visualization plugins

If you want to integrate the scientific charts in the report, you need to install the visualization plugins.

```
# Install all plugins
conda install --channel biovis-report --channel conda-forge --channel bioconda biovis-rbased-plugins 

conda install --channel biovis-report --channel conda-forge biovis-pybased-plugins 

conda install --channel biovis-report --channel conda-forge biovis-jsbased-plugins
```

!!! note

    All plugins are divided into three plugin packages depending on the development language (`biovis-rbased-plugins`, `biovis-pybased-plugins`, `biovis-jsbased-plugins`). 

    If you want to know the difference between the plugin packages, you can read <a href="/docs/plugins/" target="_blank">the plugin guide</a>.

    If you don't care the details, you can install all the three plugin packages directlly.

## Step3: Test your installation

Run the command `biovis-report -h`, You'll see the following output.

```
# Please activate the `biovis-report` environment before any other operation.
conda activate biovis-report

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

Everything is okay, you can launch an example or write your first report. Keep going on.
