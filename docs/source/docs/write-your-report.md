> How to layout and write your Markdown source files

## File layout
Please make a new clean directory as the project directory before you create a new report. All report source files, README.md and LICENSE.md need to be placed in this directory. In this document, we assume the project directory is called `biovis-report-project`.

Your report source file should be written as regular Markdown files (see Writing with Markdown below), and placed in the `report` directory. By default, this directory will be named report or whatever you like, but please keep it as short as possible without special characters, and a single word is best. And the directory will exist at the top level of your project, alongside the `LICENSE.md` and `README.md` files.

The simplest project you can create will look something like this:

```
.
├── LICENSE.md # Copyright notice, how other researchers can use your report source files and data
├── README.md  # Tell other researchers how to use your report.
└── report
    ├── data                                           # Your data files, you may use these files in plugins
    │   └── tnbcexpmelt1_tp53.rds                      # Example data file. Please use your data instead of it.
    ├── index.md
```

By convention your report homepage should be named index.md (see Index pages below for details). Any of the following file extensions may be used for your Markdown source files: markdown, mdown, mkdn, mkd, md. All Markdown files included in your report directory will be rendered in the built site regardless of any settings.

!!! note

    Files and directories with names which begin with a dot (for example: .foo.md or .bar/baz.md) are ignored by `biovis-report`, which matches the behavior of most web servers. There is no option to override this behavior.

You can also create multi-page documentation, by creating several Markdown files:

```
.
├── LICENSE.md # Copyright notice, how other researchers can use your report source files and data
├── README.md  # Tell other researchers how to use your report.
└── report
    ├── data                                           # Your data files, you may use these files in plugins
    │   └── tnbcexpmelt1_tp53.rds                      # Example data file.
    ├── index.md
    ├── about.md
    ├── license.md
```

The file layout you use determines the URLs that are used for the generated pages. Given the above layout, pages would be generated for the following URLs:

```
/
/about/
/license/
```

You can also include your Markdown files in nested directories if that better suits your report layout.

```
.
├── LICENSE.md                                         # Copyright notice, how other researchers can use your report source files and data
├── README.md                                          # Tell other researchers how to use your report.
└── report
    ├── data                                           # Your data files, you may use these files in plugins
    │   └── tnbcexpmelt1_tp53.rds                      
    ├── about
    │   └── license.md
    ├── index.md                                       # Homepage
    └── project  
        ├── clinical_data.md                           # Each markdown file will be converted to an html page.
        ├── copy_number_variation.md
        ├── expression.md
        └── single_nucleotide_polymorphism.md     
```

Source files inside nested directories will cause pages to be generated with nested URLs, like so:

```
/
/about/license/
/project/clinical_data/
/project/copy_number_variation/
/project/expression/
/project/single_nucleotide_polymorphism/
```

Any files which are not identified as Markdown files (by their file extension) within the report directory are copied by BioVisReport to the built report site unaltered. See how to link to images and media below for details.

## Index pages

When a directory is requested, by default, most web servers will return an index file (usually named index.html) contained within that directory if one exists. For that reason, the homepage in all of the examples above has been named index.md, which BioVisReport will render to index.html when building the site.

## Writing with Markdown
BioVisReport pages must be authored in Markdown, a lightweight markup language which results in easy-to-read, easy-to-write plain text documents that can be converted to valid HTML documents in a predictable manner.

BioVisReport uses the [Mkdocs](https://www.mkdocs.org/) and Python-Markdown library to render Markdown documents to HTML. Python-Markdown is almost completely compliant with the reference implementation, although there are a few very minor differences.

## Add a scientifical chart

Please see the following example snippet, a grouped-boxplot-r plugin is called in the markown code. The snippet can be generated a visualization chart as following image shown.  

```markdown
### Per Gene Expression

The description for gene expression matrix.

@grouped-boxplot-r(dataFile='./report/data/tnbcexpmelt1_tp53.rds', dataType='rds', xAxis='Group', yAxis='Value')

```

!!! note

    The `./report/data/tnbcexpmelt1_tp53.rds` is a relative path, `report` is the directory where the source files are located. Please read the [File Layout](/docs/write-your-report/#file-layout) for more details.

![Grouped Boxplot Example](/assets/images/grouped-boxplot-r-example.png)

## Launch your report on livereload mode

You need to change your working directory to the project directory in which the report is located (such as `biovis-report-project`), and launch the biovis-report on livereload mode. The report will be automatic updated when you changed the report source files and the report is launched on livereload mode.

```
# We assume your project directory is located in the `/Users/codespace/Downloads` directory.
cd /Users/codespace/Downloads/biovis-report-project

biovis-report report -t ./example -p ./ --enable-plugin --theme biovis_report -m livereload 
```

## Build your report for publishing or sharing to other researchers

```
# We assume your project directory is located in the `/Users/codespace/Downloads` directory.
cd /Users/codespace/Downloads/biovis-report-project

biovis-report report -t ./example -p ./ --enable-plugin --theme biovis_report -m build
```

After building, you will get a series of html, data, css, and javascript files as follows.
![Report HTML](/assets/images/report_html.png)