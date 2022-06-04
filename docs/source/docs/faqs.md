---
hide:
  - navigation
---

## 1. Why we use conda to install and manage BioVisReport and related dependency packages?

BioVisReport requires Python 3.7+ and a set of R/Python/JavaScript packages to be loaded in your environment in order for full functionality to work. We need a easier solution to install all the depedencies, and conda was such a solution that fit our needs (you can use minicodna/anaconda).

## 2. Why can't you open the report directly in browser?

The BioVisReport have two different forms: source files (markdown) and compiled report (html). All source files need to be compiled to a series of html before you view. And compiled report requires some advanced features of the BioVisReport to be opened and viewed by the browser.

For easier to view and publish compiled report, we provide a [biovis-report-viewer](/docs/write-your-report/).

## 3. Why do we need `biovis-report` and `biovis-report-viewer`?

`biovis-report` is a development kits, it contains development server and a series of interactive chart plugins. so you can write your report with markdown, compile the report source files to a series of html, and view the report on browser. However, your reports cannot always be run in development mode.

`biovis-report-viewer` is a viewer for viewing your compiled report. Please use it when:

- Publish your compiled report online.

- Get a compiled report from other researchers.

## 4. Why the browser complain "Did you mean biovis.report" when you click the "the Online Example" link?

You may see something as the following image. Don't worry about it, it's not a fake website.

Because we implemented a code level redirect and the BioVisReport website url (`https://biovis.report`) have a different top-level domain with the online example website (`https://biovis-report-example1.3steps.cn/`).

If you worry about it, please visit [`https://biovis-report-example1.3steps.cn/`](`https://biovis-report-example1.3steps.cn/`) directly.

<figure markdown>
  ![Figure](/assets/images/error.png){ width="50%" }
</figure>
