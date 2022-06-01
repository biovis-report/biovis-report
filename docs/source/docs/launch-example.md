## Step 1: Download the example source files

Please download <a href="https://github.com/biovis-report/biovis-report-example/archive/refs/heads/master.zip">the example archive file</a> and unzip it.

Or

If you have `git` on your machine, you can clone [the example repo](https://github.com/biovis-report/biovis-report-example) to taste the biovis-report.

```
git clone https://github.com/biovis-report/biovis-report-example
```

## Step 2: Understand the structure and content of the report

Locate your download and change the working directory to it. e.g. the `biovis-report-example` is located in the `/Users/codespace/Downloads/biovis-report-example`. The subdirectory `example` has source files and example data. A well-structured report usually contains the following documents and organizes all the documents in the report in the way shown in the picture below.

```
.
├── LICENSE.md                                         # Copyright notice, how other researchers can use your report source files and data
├── README.md                                          # Tell other researchers how to use your report.
└── example
    ├── about
    │   └── license.md
    ├── assets
    │   └── abstract.png
    ├── data                                           # Data Directory, Each data file can be referenced by the plugin in the markdown file. The data file format depends on the requirements of the plugin, but csv, tsv are usually supported 
    │   ├── Somatic_Mutationfrequency_all.rds
    │   ├── Somatic_Mutationfrequency_top20.rds
    │   ├── clinical_rocket_all.rds
    │   ├── data_clinical_patient.csv
    │   ├── heatmaptt10.rds
    │   ├── heatmaptt100.rds
    │   ├── heatmaptt1000.rds
    │   ├── meta_and_clinical_data_table_short_c8.csv
    │   ├── somatic_freq_top.csv
    │   ├── tnbcexp_20_m0sd1_heatmap.rds
    │   ├── tnbcexpmelt1_tp53.rds
    │   └── tnbcexpmelt_top19.rds
    ├── defaults                                       # A default config for biovis-report
    ├── index.md                                       # Homepage
    └── project                                        # The project subdirectory will be a menu on the report website, you can have several subdirectory with different directory name.
        ├── clinical_data.md                           # Each markdown file will be converted to an html page.
        ├── copy_number_variation.md
        ├── expression.md
        └── single_nucleotide_polymorphism.md

5 directories, 22 files
```

## Step 3: Launch the example
You need to change your working directory to `biovis-report-example`, and launch the biovis-report on livereload mode.

```
cd /Users/codespace/Downloads/biovis-report-example

biovis-report report -t ./example -m livereload -p ./ --enable-plugin --theme biovis_report
```