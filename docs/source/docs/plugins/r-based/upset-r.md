### ShowCase

Online example will be available soon.

<img src="/assets/images/plugins/upset-r.png">

### Description
Interactive upset plot visualization from a Shiny app(r version).

### Example Data
```
                              Name   ReleaseDate Action Adventure Children
                  Toy Story (1995)        1995      0         0        1
                    Jumanji (1995)        1995      0         1        1
           Grumpier Old Men (1995)        1995      0         0        0
          Waiting to Exhale (1995)        1995      0         0        0
Father of the Bride Part II (1995)        1995      0         0        0
                       Heat (1995)        1995      1         0        0
                    Sabrina (1995)        1995      0         0        0
               Tom and Huck (1995)        1995      0         1        1
               Sudden Death (1995)        1995      1         0        0
                  GoldenEye (1995)        1995      1         1        0
```

### Usage

```
@upset-r(dataFile='movies.rds', dataType='rds', title='',
         showEmptyInterSec=True, showBarNumbers=True, setSort=True,
         nIntersects=10, assignmentType='upset', subtitle='', text='',
         showpanel=True)
```

### Arguments

```ini
; Configuration for Scatter Chart
[data]
; input data, may be a file or other data source.
; input data must be tidy data.
dataFile = movies.rds
; data file format
dataType = rds

[attributes]
; Shiny app title
title =
showEmptyInterSec = True
showBarNumbers = True
setSort = True
nIntersects = 10
; choices: ('upset', 'all')
assignmentType = upset
; query url
queryURL = https://www.duckduckgo.com/?q=
; subtitle and text for scatter chart
subtitle =
text =
showpanel = True
```

### Value
An interactive upset plot.

### Author(s)
Jingcheng Yang(yjcyxky@163.com)

### Examples

```
# If you need to show a default interactive plot by using sample data
@upset-r()

# If you have a custom data, you need to reset these arguments at least.
@upset-r(dataFile='violin_plot.rds', dataType='rds')
```