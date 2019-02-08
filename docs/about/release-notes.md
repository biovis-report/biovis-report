# Release Notes

---

## Upgrading

To upgrade MkDocs to the latest version, use pip:

    pip install -U mkdocs

You can determine your currently installed version using `mkdocs --version`:

    $ mkdocs --version
    mkdocs, version 1.0 from /path/to/mkdocs (Python 3.6)

## Maintenance team

The current and past members of the MkDocs team.

* [@tomchristie](https://github.com/tomchristie/)
* [@d0ugal](https://github.com/d0ugal/)
* [@waylan](https://github.com/waylan/)

## Version 1.1 (*in development*)

### Major Additions to Version 1.1

#### Support for Lunr.py as `prebuild_index` engine

Mkdocs now supports prebuilding indices using [Lunr.py][lunrpy-docs], a pure
Python implementation of Lunr.js, allowing the user to avoid installing a
NodeJS environment if so desired. For more information please read the
[`prebuild_index` documentation][prebuildindex-docs].

[lunrpy-docs]: http://lunr.readthedocs.io/
[prebuildindex-docs]: ../../user-guide/configuration/#prebuild_index

#### `readthedocs` theme updated with upstream (#588 and #1374)

The `readthedocs` theme now more closely matches the [upstream] Sphinx theme
(version 0.4.1). A number of new theme configuration settings were added which
mirror the upstream configuration options. See the [theme
documentation][rtd-docs] for details.

[upstream]: https://github.com/rtfd/sphinx_rtd_theme/
[rtd-docs]: ../user-guide/styling-your-docs.md#readthedocs

## Update `mkdocs` theme to bootswatch 4.1.3 (#1563)

The `mkdocs` theme now supports all the features of [Bootswatch 4.1]. Note that
the [dropdowns] used in the navigation only support one level of nesting. If
your global navigation uses more than one level, things will likely be broken.

[Bootswatch 4.1]: https://getbootstrap.com/docs/4.1/getting-started/introduction/
[dropdowns]: https://getbootstrap.com/docs/4.1/components/navs/#pills-with-dropdowns

### Other Changes and Additions to Version 1.1

* Bugfix: Account for encoded URLs (#1670).
* Bugfix: Ensure theme files do not override `docs_dir` files (#1671).
* Bugfix: Do not normalize URL fragments (#1655).
* Add canonical tag to `readthedocs` theme (#1669).

## Version 1.0.4 (2018-09-07)

* Bugfix: Ignore absolute links in Markdown (#1621).

## Version 1.0.3 (2018-08-29)

* Bugfix: Warn on relative paths in navigation (#1604).
* Bugfix: Handle empty `theme_config.yml` files correctly (#1602).

## Version 1.0.2 (2018-08-22)

* Bugfix: Provide absolute `base_url` to error templates (#1598).

## Version 1.0.1 (2018-08-13)

* Bugfix: Prevent page reload when [Enter] is pressed in search box (#1589).
* Bugfix: Avoid calling `search` until all assets are ready (#1584).
* Bugfix: Exclude `README.md` if `index.md` is present (#1580).
* Bugfix: Fix `readthedocs` theme navigation bug with homepage (#1576).

## Version 1.0 (2018-08-03)

### Major Additions to Version 1.0

#### Internal Refactor of Pages, Files, and Navigation

Internal handling of pages, files and navigation has been completely refactored.
The changes included in the refactor are summarized below.

* Support for hidden pages. All Markdown pages are now included in the build
  regardless of whether they are included in the navigation configuration
  (#699).
* The navigation can now include links to external sites (#989 #1373 & #1406).
* Page data (including titles) is properly determined for all pages before any
  page is rendered (#1347).
* Automatically populated navigation now sorts index pages to the top. In other
  words, The index page will be listed as the first child of a directory, while
  all other documents are sorted alphanumerically by file name after the index
  page (#73 & #1042).
* A `README.md` file is now treated as an index file within a directory and
  will be rendered to `index.html` (#608).
* The URLs for all files are computed once and stored in a files collection.
  This ensures all internal links are always computed correctly regardless of
  the configuration. This also allows all internal links to be validated, not
  just links to other Markdown pages. (#842 & #872).
* A new [url] template filter smartly ensures all URLs are relative to the
  current page (#1526).
* An [on_files] plugin event has been added, which could be used to include
  files not in the `docs_dir`, exclude files, redefine page URLs (i.e.
  implement extensionless URLs), or to manipulate files in various other ways.

  [on_files]: ../user-guide/plugins.md#on_files

##### Backward Incompatible Changes

As part of the internal refactor, a number of backward incompatible changes have
been introduced, which are summarized below.

###### URLS have changed when `use_directory_urls` is `False`

Previously, all Markdown pages would be have their filenames altered to be index
pages regardless of how the [use_directory_urls] setting was configured.
However, the path munging is only needed when `use_directory_urls` is set to
`True` (the default). The path mungling no longer happens when
`use_directory_urls` is set to `False`, which will result in different URLs for
all pages that were not already index files. As this behavior only effects a
non-default configuration, and the most common user-case for setting the option
to `False` is for local file system (`file://`) browsing, its not likely to
effect most users. However, if you have `use_directory_urls` set to `False`
for a MkDocs site hosted on a web server, most of your URLs will now be broken.
As you can see below, the new URLs are much more sensible.

| Markdown file   | Old URL              | New URL        |
| --------------- | -------------------- | -------------- |
| `index.md`      | `index.html`         | `index.html`   |
| `foo.md`        | `foo/index.html`     | `foo.html`     |
| `foo/bar.md`    | `foo/bar/index.html` | `foo/bar.html` |

Note that there has been no change to URLs or file paths when
`use_directory_urls` is set to `True` (the default), except that MkDocs more
consistently includes an ending slash on all internally generated URLs.

[use_directory_urls]: ../user-guide/configuration.md#use_directory_urls

###### The `pages` configuration setting has been renamed to `nav`

The `pages` configuration setting is deprecated and will issue a warning if set
in the configuration file. The setting has been renamed `nav`. To update your
configuration, simply rename the setting to `nav`. In other words, if your
configuration looked like this:

```yaml
pages:
    - Home: index.md
    - User Guide: user-guide.md
```

Simply edit the configuration as follows:

```yaml
nav:
    - Home: index.md
    - User Guide: user-guide.md
```

In the current release, any configuration which includes a `pages` setting, but
no `nav` setting, the `pages` configuration will be copied to `nav` and a
warning will be issued. However, in a future release, that may no longer happen.
If both `pages` and `nav` are defined, the `pages` setting will be ignored.

###### Template variables and `base_url`

In previous versions of MkDocs some URLs expected the [base_url] template
variable to be prepended to the URL and others did not. That inconsistency has
been removed in that no URLs are modified before being added to the template
context.

For example, a theme template might have previously included a link to
the `site_name` as:

```django
<a href="{{ nav.homepage.url }}">{{ config.site_name }}</a>
```

And MkDocs would magically return a URL for the homepage which was relative to
the current page. That "magic" has been removed and the [url] template filter
should be used:

```django
<a href="{{ nav.homepage.url|url }}">{{ config.site_name }}</a>
```

This change applies to any navigation items and pages, as well as the
`page.next_page` and `page.previous_page` attributes. For the time being, the
`extra_javascript` and `extra_css` variables continue to work as previously
(without the `url` template filter), but they have been deprecated and the
corresponding configuration values (`config.extra_javascript` and
`config.extra_css` respectively) should be used with the filter instead.

```django
{% for path in config['extra_css'] %}
    <link href="{{ path|url }}" rel="stylesheet">
{% endfor %}
```

Note that navigation can now include links to external sites. Obviously, the
`base_url` should not be prepended to these items. However, the `url` template
filter is smart enough to recognize the URL is absolute and does not alter it.
Therefore, all navigation items can be passed to the filter and only those that
need to will be altered.

```django
{% for nav_item in nav %}
    <a href="{{ nav_item.url|url }}">{{ nav_item.title }}</a>
{% endfor %}
```

[base_url]: ../user-guide/custom-themes.md#base_url
[url]: ../user-guide/custom-themes.md#url

#### Path Based Settings are Relative to Configuration File (#543)

Previously any relative paths in the various configuration options were
resolved relative to the current working directory. They are now resolved
relative to the configuration file. As the documentation has always encouraged
running the various MkDocs commands from the directory that contains the
configuration file (project root), this change will not affect most users.
However, it will make it much easier to implement automated builds or otherwise
run commands from a location other than the project root.

Simply use the `-f/--config-file` option and point it at the configuration file:

```sh
mkdocs build --config-file /path/to/my/config/file.yml
```

As previously, if no file is specified, MkDocs looks for a file named
`mkdocs.yml` in the current working directory.

#### Added support for YAML Meta-Data (#1542)

Previously, MkDocs only supported MultiMarkdown style meta-data, which does not
recognize different data types and is rather limited. MkDocs now also supports
YAML style meta-data in Markdown documents. MkDocs relies on the the presence or
absence of the deliminators (`---` or `...`) to determine whether YAML style
meta-data or MultiMarkdown style meta-data is being used.

Previously MkDocs would recognize MultiMarkdown style meta-data between the
deliminators. Now, if the deliminators are detected, but the content between the
deliminators is not valid YAML meta-data, MkDocs does not attempt to parse the
content as MultiMarkdown style meta-data. Therefore, MultiMarkdowns style
meta-data must not include the deliminators. See the [MultiMarkdown style
meta-data documentation] for details.

Prior to version 0.17, MkDocs returned all meta-data values as a list of strings
(even a single line would return a list of one string). In version 0.17, that
behavior was changed to return each value as a single string (multiple lines
were joined), which some users found limiting (see #1471). That behavior
continues for MultiMarkdown style meta-data in the current version. However,
YAML style meta-data supports the full range of "safe" YAML data types.
Therefore, it is recommended that any complex meta-data make use of the YAML
style (see the [YAML style meta-data documentation] for details). In fact, a
future version of MkDocs may deprecate support for MultiMarkdown style
meta-data.

[MultiMarkdown style meta-data documentation]: ../user-guide/writing-your-docs.md#multimarkdown-style-meta-data
[YAML style meta-data documentation]: ../user-guide/writing-your-docs.md#yaml-style-meta-data

#### Refactor Search Plugin

The search plugin has been completely refactored to include support for the
following features:

* Use a web worker in the browser with a fallback (#1396).
* Optionally pre-build search index locally (#859 & #1061).
* Upgrade to lunr.js 2.x (#1319).
* Support search in languages other than English (#826).
* Allow the user to define the word separators (#867).
* Only run searches for queries of length > 2 (#1127).
* Remove dependency on require.js (#1218).
* Compress the search index (#1128).

Users can review the [configuration options][search config] available and theme
authors should review how [search and themes] interact.

[search config]: ../user-guide/configuration.md#search
[search and themes]: ../user-guide/custom-themes.md#search_and_themes

#### `theme_dir` Configuration Option fully Deprecated

As of version 0.17, the [custom_dir] option replaced the deprecated `theme_dir`
option. If users had set the `theme_dir` option, MkDocs version 0.17 copied the
value to the `theme.custom_dir` option and a warning was issued. As of version
1.0, the value is no longer copied and an error is raised.

### Other Changes and Additions to Version 1.0

* Keyboard shortcuts changed to not conflict with commonly used accessibility
  shortcuts (#1502.)
* User friendly YAML parse errors (#1543).
* Officially support Python 3.7.
* A missing theme configuration file now raises an error.
* Empty `extra_css` and `extra_javascript` settings no longer raise a warning.
* Add highlight.js configuration settings to built-in themes (#1284).
* Close search modal when result is selected (#1527).
* Add a level attribute to AnchorLinks (#1272).
* Add MkDocs version check to gh-deploy script (#640).
* Improve Markdown extension error messages. (#782).
* Drop official support for Python 3.3 and set `tornado>=5.0` (#1427).
* Add support for GitLab edit links (#1435).
* Link to GitHub issues from release notes (#644).
* Expand {sha} and {version} in gh-deploy commit message (#1410).
* Compress `sitemap.xml` (#1130).
* Defer loading JS scripts (#1380).
* Add a title attribute to the search input (#1379).
* Update RespondJS to latest version (#1398).
* Always load Google Analytics over HTTPS (#1397).
* Improve scrolling frame rate (#1394).
* Provide more version info. (#1393).
* Refactor `writing-your-docs.md` (#1392).
* Workaround Safari bug when zooming to &lt; 100% (#1389).
* Remove addition of `clicky` class to body and animations. (#1387).
* Prevent search plugin from reinjecting `extra_javascript` files (#1388).
* Refactor `copy_media_files` util function for more flexibility (#1370).
* Remove PyPI Deployment Docs (#1360).
* Update links to Python-Markdown library (#1360).
* Document how to generate manpages for MkDocs commands (#686).

## Version 0.17.5 (2018-07-06)

* Bugfix: Fix Python 3.7 and PEP 479 incompatibility (#1518).

## Version 0.17.4 (2018-06-08)

* Bugfix: Add multi-level nesting support to sitemap.xml (#1482).

## Version 0.17.3 (2018-03-07)

* Bugfix: Set dependency `tornado>=4.1,<5.0` due to changes in 5.0 (#1428).

## Version 0.17.2 (2017-11-15)

* Bugfix: Correct `extra_*` config setting regressions (#1335 & #1336).

## Version 0.17.1 (2017-10-30)

* Bugfix: Support `repo_url` with missing ending slash. (#1321).
* Bugfix: Add length support to `mkdocs.toc.TableOfContext` (#1325).
* Bugfix: Add some theme specific settings to the search plugin for third party
  themes (#1316).
* Bugfix: Override `site_url` with `dev_addr` on local server (#1317).

## Version 0.17.0 (2017-10-19)

### Major Additions to Version 0.17.0

#### Plugin API. (#206)

A new [Plugin API] has been added to MkDocs which allows users to define their
own custom behaviors. See the included documentation for a full explanation of
the API.

The previously built-in search functionality has been removed and wrapped in a
plugin (named "search") with no changes in behavior. When MkDocs builds, the
search index is now written to `search/search_index.json` instead of
`mkdocs/search_index.json`. If no plugins setting is defined in the config,
then the `search` plugin will be included by default. See the
[configuration][plugin_config] documentation for information on overriding the
default.

[Plugin API]: ../user-guide/plugins.md
[plugin_config]: ../user-guide/configuration.md#plugins

#### Theme Customization. (#1164)

Support had been added to provide theme specific customizations. Theme authors
can define default options as documented in [Theme Configuration]. A theme can
now inherit from another theme, define various static templates to be rendered,
and define arbitrary default variables to control behavior in the templates.
The theme configuration is defined in a configuration file named
`mkdocs_theme.yml` which should be placed at the root of your template files. A
warning will be raised if no configuration file is found and an error will be
raised in a future release.

Users can override those defaults under the [theme] configuration option of
their `mkdocs.yml` configuration file, which now accepts nested options. One
such nested option is the [custom_dir] option, which replaces the now deprecated
`theme_dir` option. If users had previously set the `theme_dir` option, a
warning will be issued, with an error expected in a future release.

If a configuration previously defined a `theme_dir` like this:

```yaml
theme: mkdocs
theme_dir: custom
```

Then the configuration should be adjusted as follows:

```yaml
theme:
    name: mkdocs
    custom_dir: custom
```

See the [theme] configuration option documentation for details.

[Theme Configuration]: ../user-guide/custom-themes.md#theme-configuration
[theme]: ../user-guide/configuration.md#theme
[custom_dir]: ../user-guide/configuration.md#custom_dir

#### Previously deprecated Template variables removed. (#1168)

##### Page Template

The primary entry point for page templates has been changed from `base.html` to
`main.html`. This allows `base.html` to continue to exist while allowing users
to override `main.html` and extend `base.html`. For version 0.16, `base.html`
continued to work if no `main.html` template existed, but it raised a
deprecation warning. In version 1.0, a build will fail if no `main.html`
template exists.

##### Context Variables

Page specific variable names in the template context have been refactored as
defined in [Custom Themes](../user-guide/custom-themes.md#page). The
old variable names issued a warning in version 0.16, but have been removed in
version 1.0.

Any of the following old page variables should be updated to the new ones in
user created and third-party templates:

| Old Variable Name | New Variable Name   |
| ----------------- | ------------------- |
| current_page      | [page]              |
| page_title        | [page.title]        |
| content           | [page.content]      |
| toc               | [page.toc]          |
| meta              | [page.meta]         |
| canonical_url     | [page.canonical_url]|
| previous_page     | [page.previous_page]|
| next_page         | [page.next_page]    |

[page]: ../user-guide/custom-themes.md#page
[page.title]: ../user-guide/custom-themes.md#pagetitle
[page.content]: ../user-guide/custom-themes.md#pagecontent
[page.toc]: ../user-guide/custom-themes.md#pagetoc
[page.meta]: ../user-guide/custom-themes.md#pagemeta
[page.canonical_url]: ../user-guide/custom-themes.md#pagecanonical_url
[page.previous_page]: ../user-guide/custom-themes.md#pageprevious_page
[page.next_page]: ../user-guide/custom-themes.md#pagenext_page

Additionally, a number of global variables have been altered and/or removed
and user created and third-party templates should be updated as outlined below:

| Old Variable Name | New Variable Name or Expression        |
| ----------------- | -------------------------------------- |
| current_page      | page                                   |
| include_nav       | nav&#124;length&gt;1                   |
| include_next_prev | (page.next_page or page.previous_page) |
| site_name         | config.site_name                       |
| site_author       | config.site_author                     |
| page_description  | config.site_description                |
| repo_url          | config.repo_url                        |
| repo_name         | config.repo_name                       |
| site_url          | config.site_url                        |
| copyright         | config.copyright                       |
| google_analytics  | config.google_analytics                |
| homepage_url      | nav.homepage.url                       |
| favicon           | {{ base_url }}/img/favicon.ico         |

#### Auto-Populated extra_css and extra_javascript Fully Deprecated. (#986)

In previous versions of MkDocs, if the `extra_css` or `extra_javascript` config
settings were empty, MkDocs would scan the `docs_dir` and auto-populate each
setting with all of the CSS and JavaScript files found. On version 0.16 this
behavior was deprecated and a warning was issued. In 0.17 any unlisted CSS and
JavaScript files will not be included in the HTML templates, however, a warning
will be issued. In other words, they will still be copied to the `site-dir`, but
they will not have any effect on the theme if they are not explicitly listed.

All CSS and javaScript files in the `docs_dir` should be explicitly listed in
the `extra_css` or `extra_javascript` config settings going forward.

### Other Changes and Additions to Version 0.17.0

* Add "edit Link" support to MkDocs theme (#1129)
* Open files with `utf-8-sig` to account for BOM (#1186)
* Symbolic links are now followed consistently (#1134)
* Support for keyboard navigation shortcuts added to included themes (#1095)
* Some refactoring and improvements to config_options (#1296)
* Officially added support for Python 3.6 (#1296)
* 404 Error page added to readthedocs theme (#1296))
* Internal refactor of Markdown processing (#713)
* Removed special error message for mkdocs-bootstrap and mkdocs-bootswatch
  themes (#1168)
* The legacy pages config is no longer supported (#1168)
* The deprecated `json` command has been removed (#481)
* Support for Python 2.6 has been dropped (#165)
* File permissions are no longer copied during build (#1292)
* Support query and fragment strings in `edit_uri` (#1224 & #1273)

## Version 0.16.3 (2017-04-04)

* Fix error raised by autoscrolling in the readthedocs theme (#1177)
* Fix a few documentation typos (#1181 & #1185)
* Fix a regression to livereload server introduced in 0.16.2 (#1174)

## Version 0.16.2 (2017-03-13)

* System root (`/`) is not a valid path for site_dir or docs_dir (#1161)
* Refactor readthedocs theme navigation (#1155 & #1156)
* Add support to dev server to serve custom error pages (#1040)
* Ensure nav.homepage.url is not blank on error pages (#1131)
* Increase livereload dependency to 2.5.1 (#1106)

## Version 0.16.1 (2016-12-22)

* Ensure scrollspy behavior does not affect nav bar (#1094)
* Only "load" a theme when it is explicitly requested by the user (#1105)

## Version 0.16 (2016-11-04)

### Major Additions to Version 0.16.0

#### Template variables refactored. (#874)

##### Page Context

Page specific variable names in the template context have been refactored as
defined in [Custom Themes](../user-guide/custom-themes.md#page). The
old variable names will issue a warning but continue to work for version 0.16,
but may be removed in a future version.

Any of the following old page variables should be updated to the new ones in
user created and third-party templates:

| Old Variable Name | New Variable Name   |
| ----------------- | ------------------- |
| current_page      | [page]              |
| page_title        | [page.title]        |
| content           | [page.content]      |
| toc               | [page.toc]          |
| meta              | [page.meta]         |
| canonical_url     | [page.canonical_url]|
| previous_page     | [page.previous_page]|
| next_page         | [page.next_page]    |

[page]: ../user-guide/custom-themes.md#page
[page.title]: ../user-guide/custom-themes.md#pagetitle
[page.content]: ../user-guide/custom-themes.md#pagecontent
[page.toc]: ../user-guide/custom-themes.md#pagetoc
[page.meta]: ../user-guide/custom-themes.md#pagemeta
[page.canonical_url]: ../user-guide/custom-themes.md#pagecanonical_url
[page.previous_page]: ../user-guide/custom-themes.md#pageprevious_page
[page.next_page]: ../user-guide/custom-themes.md#pagenext_page

##### Global Context

Additionally, a number of global variables have been altered and/or deprecated
and user created and third-party templates should be updated as outlined below:

Previously, the global variable `include_nav` was altered programmatically based
on the number of pages in the nav. The variable will issue a warning but
continue to work for version 0.16, but may be removed in a future version. Use
`{% if nav|length>1 %}` instead.

Previously, the global variable `include_next_prev` was altered programmatically
based on the number of pages in the nav. The variable will issue a warning but
continue to work for version 0.16, but may be removed in a future version. Use
`{% if page.next_page or page.previous_page %}` instead.

Previously the global variable `page_description` was altered programmatically
based on whether the current page was the homepage. Now it simply maps to
`config['site_description']`. Use `{% if page.is_homepage %}` in the template to
conditionally change the description.

The global variable `homepage_url` maps directly to `nav.homepage.url` and is
being deprecated. The variable will issue a warning but continue to work for
version 0.16, but may be removed in a future version. Use `nav.homepage.url`
instead.

The global variable `favicon` maps to the configuration setting `site_favicon`.
Both the template variable and the configuration setting are being deprecated
and will issue a warning but continue to work for version 0.16, and may be
removed in a future version. Use `{{ base_url }}/img/favicon.ico` in your
template instead. Users can simply save a copy of their custom favicon icon to
`img/favicon.ico` in either their `docs_dir` or `theme_dir`.

A number of variables map directly to similarly named variables in the `config`.
Those variables are being deprecated and will issue a warning but continue to
work for version 0.16, but may be removed in a future version. Use
`config.var_name` instead, where `var_name` is the name of one of the
[configuration] variables.

[configuration]: /user-guide/configuration.md

Below is a summary of all of the changes made to the global context:

| Old Variable Name | New Variable Name or Expression        |
| ----------------- | -------------------------------------- |
| current_page      | page                                   |
| include_nav       | nav&#124;length&gt;1                   |
| include_next_prev | (page.next_page or page.previous_page) |
| site_name         | config.site_name                       |
| site_author       | config.site_author                     |
| page_description  | config.site_description                |
| repo_url          | config.repo_url                        |
| repo_name         | config.repo_name                       |
| site_url          | config.site_url                        |
| copyright         | config.copyright                       |
| google_analytics  | config.google_analytics                |
| homepage_url      | nav.homepage.url                       |
| favicon           | {{ base_url }}/img/favicon.ico         |

#### Increased Template Customization. (#607)

The built-in themes have been updated by having each of their many parts wrapped
in template blocks which allow each individual block to be easily overridden
using the `theme_dir` config setting. Without any new settings, you can use a
different analytics service, replace the default search function, or alter the
behavior of the navigation, among other things. See the relevant
[documentation][blocks] for more details.

To enable this feature, the primary entry point for page templates has been
changed from `base.html` to `main.html`. This allows `base.html` to continue to
exist while allowing users to override `main.html` and extend `base.html`. For
version 0.16, `base.html` will continue to work if no `main.html` template
exists, but it is deprecated and will raise a warning. In version 1.0, a build
will fail if no `main.html` template exists. Any custom and third party
templates should be updated accordingly.

The easiest way for a third party theme to be updated would be to simply add a
`main.html` file which only contains the following line:

```django
{% extends "base.html" %}
```

That way, the theme contains the `main.html` entry point, and also supports
overriding blocks in the same manner as the built-in themes. Third party themes
are encouraged to wrap the various pieces of their templates in blocks in order
to support such customization.

[blocks]: ../user-guide/styling-your-docs.md#overriding-template-blocks

#### Auto-Populated `extra_css` and `extra_javascript` Deprecated. (#986)

In previous versions of MkDocs, if the `extra_css` or `extra_javascript` config
settings were empty, MkDocs would scan the `docs_dir` and auto-populate each
setting with all of the CSS and JavaScript files found. This behavior is
deprecated and a warning will be issued. In the next release, the auto-populate
feature will stop working and any unlisted CSS and JavaScript files will not be
included in the HTML templates. In other words, they will still be copied to the
`site-dir`, but they will not have any effect on the theme if they are not
explicitly listed.

All CSS and javaScript files in the `docs_dir` should be explicitly listed in
the `extra_css` or `extra_javascript` config settings going forward.

#### Support for dirty builds. (#990)

For large sites the build time required to create the pages can become problematic,
thus a "dirty" build mode was created. This mode simply compares the modified time
of the generated HTML and source markdown. If the markdown has changed since the
HTML then the page is re-constructed. Otherwise, the page remains as is. This mode
may be invoked in both the `mkdocs serve` and `mkdocs build` commands:

```text
mkdocs serve --dirtyreload
```

```text
mkdocs build --dirty
```

It is important to note that this method for building the pages is for development
of content only, since the navigation and other links do not get updated on other
pages.

#### Stricter Directory Validation

Previously, a warning was issued if the `site_dir` was a child directory of the
`docs_dir`. This now raises an error. Additionally, an error is now raised if
the `docs_dir` is set to the directory which contains your config file rather
than a child directory. You will need to rearrange you directory structure to
better conform with the documented [layout].

[layout]: ../user-guide/writing-your-docs.md#file-layout

### Other Changes and Additions to Version 0.16.0

* Bugfix: Support `gh-deploy` command on Windows with Python 3 (#722)
* Bugfix: Include .woff2 font files in Python package build (#894)
* Various updates and improvements to Documentation Home Page/Tutorial (#870)
* Bugfix: Support livereload for config file changes (#735)
* Bugfix: Non-media template files are no longer copied with media files (#807)
* Add a flag (-e/--theme-dir) to specify theme directory with the commands
  `mkdocs build` and `mkdocs serve` (#832)
* Fixed issues with Unicode file names under Windows and Python 2. (#833)
* Improved the styling of in-line code in the MkDocs theme. (#718)
* Bugfix: convert variables to JSON when being passed to JavaScript (#850)
* Updated the ReadTheDocs theme to match the upstream font sizes and colors
  more closely. (#857)
* Fixes an issue with permalink markers showing when the mouse was far above
  them (#843)
* Bugfix: Handle periods in directory name when automatically creating the
  pages config. (#728)
* Update searching to Lunr 0.7, which comes with some performance enhancements
  for larger documents (#859)
* Bugfix: Support SOURCE_DATE_EPOCH environment variable for "reproducible"
  builds (#938)
* Follow links when copying media files (#869).
* Change "Edit on..." links to point directly to the file in the source
  repository, rather than to the root of the repository (#975), configurable
  via the new [`edit_uri`](../user-guide/configuration.md#edit_uri) setting.
* Bugfix: Don't override config value for strict mode if not specified on CLI
  (#738).
* Add a `--force` flag to the `gh-deploy` command to force the push to the
  repository (#973).
* Improve alignment for current selected menu item in readthedocs theme (#888).
* `http://user.github.io/repo` => `https://user.github.io/repo/` (#1029).
* Improve installation instructions (#1028).
* Account for wide tables and consistently wrap inline code spans (#834).
* Bugfix: Use absolute URLs in nav & media links from error templates (#77).

## Version 0.15.3 (2016-02-18)

* Improve the error message the given theme can't be found.
* Fix an issue with relative symlinks (#639)

## Version 0.15.2 (2016-02-08)

* Fix an incorrect warning that states external themes [will be removed from
  MkDocs](#add-support-for-installable-themes).

## Version 0.15.1 (2016-01-30)

* Lower the minimum supported Click version to 3.3 for package maintainers.
  (#763)

## Version 0.15.0 (2016-01-21)

### Major Additions to Version 0.15.0

#### Add support for installable themes

MkDocs now supports themes that are distributed via Python packages. With this
addition, the Bootstrap and Bootswatch themes have been moved to external git
repositories and python packages. See their individual documentation for more
details about these specific themes.

* [MkDocs Bootstrap]
* [MkDocs Bootswatch]

[MkDocs Bootstrap]: https://mkdocs.github.io/mkdocs-bootstrap/
[MkDocs Bootswatch]: https://mkdocs.github.io/mkdocs-bootswatch/

They will be included with MkDocs by default until a future release. After that
they will be installable with pip: `pip install mkdocs-bootstrap` and `pip
install mkdocs-bootswatch`

See the documentation for [Styling your docs] for more information about using
and customizing themes and [Custom themes] for creating and distributing new
themes

[Styling your docs]: ../user-guide/styling-your-docs.md
[Custom themes]: ../user-guide/custom-themes.md

### Other Changes and Additions to Version 0.15.0

* Fix issues when using absolute links to Markdown files. (#628)
* Deprecate support of Python 2.6, pending removal in 1.0.0. (#165)
* Add official support for Python version 3.5.
* Add support for [site_description] and [site_author] to the [ReadTheDocs]
  theme. (#631)
* Update FontAwesome to 4.5.0. (#789)
* Increase IE support with X-UA-Compatible. (#785)
* Added support for Python's `-m` flag. (#706)
* Bugfix: Ensure consistent ordering of auto-populated pages. (#638)
* Bugfix: Scroll the tables of contents on the MkDocs theme if it is too long
  for the page. (#204)
* Bugfix: Add all ancestors to the page attribute `ancestors` rather than just
  the initial one. (#693)
* Bugfix: Include HTML in the build output again. (#691)
* Bugfix: Provide filename to Read the Docs. (#721 and RTD#1480)
* Bugfix: Silence Click's unicode_literals warning. (#708)

[site_description]: ../user-guide/configuration.md#site_description
[site_author]: ../user-guide/configuration.md#site_author
[ReadTheDocs]: ../user-guide/styling-your-docs.md#readthedocs

## Version 0.14.0 (2015-06-09)

* Improve Unicode handling by ensuring that all config strings are loaded as
  Unicode. (#592)
* Remove dependency on the six library. (#583)
* Remove dependency on the ghp-import library. (#547)
* Add `--quiet` and `--verbose` options to all sub-commands. (#579)
* Add short options (`-a`) to most command line options. (#579)
* Add copyright footer for readthedocs theme. (#568)
* If the requested port in `mkdocs serve` is already in use, don't show the
  user a full stack trace. (#596)
* Bugfix: Fix a JavaScript encoding problem when searching with spaces. (#586)
* Bugfix: gh-deploy now works if the mkdocs.yml is not in the git repo root.
  (#578)
* Bugfix: Handle (pass-through instead of dropping) HTML entities while
  parsing TOC. (#612)
* Bugfix: Default extra_templates to an empty list, don't automatically
  discover them. (#616)

## Version 0.13.3 (2015-06-02)

* Bugfix: Reduce validation error to a warning if the site_dir is within
  the docs_dir as this shouldn't cause any problems with building but will
  inconvenience users building multiple times. (#580)

## Version 0.13.2 (2015-05-30)

* Bugfix: Ensure all errors and warnings are logged before exiting. (#536)
* Bugfix: Fix compatibility issues with ReadTheDocs. (#554)

## Version 0.13.1 (2015-05-27)

* Bugfix: Fix a problem with minimal configurations which only contain a list
  of paths in the pages config. (#562)

## Version 0.13.0 (2015-05-26)

### Deprecations to Version 0.13.0

#### Deprecate the JSON command

In this release the  `mkdocs json` command has been marked as deprecated and
when used a deprecation warning will be shown. It will be removed in a [future
release] of MkDocs, version 1.0 at the latest. The `mkdocs json` command
provided  a convenient way for users to output the documentation contents as
JSON files but with the additions of search to MkDocs this functionality is
duplicated.

A new index with all the contents from a MkDocs build is created in the
[site_dir], so with the default value for the `site_dir` It can be found in
`site/mkdocs/search_index.json`.

This new file is created on every MkDocs build (with `mkdocs build`) and
no configuration is needed to enable it.

[future release]: https://github.com/mkdocs/mkdocs/pull/481
[site_dir]: ../user-guide/configuration.md#site_dir

#### Change the pages configuration

Provide a [new way] to define pages, and specifically [nested pages], in the
mkdocs.yml file and deprecate the existing approach, support will be removed
with MkDocs 1.0.

[new way]: ../user-guide/writing-your-docs.md#configure-pages-and-navigation
[nested pages]: ../user-guide/writing-your-docs.md#multilevel-documentation

#### Warn users about the removal of builtin themes

All themes other than mkdocs and readthedocs will be moved into external
packages in a future release of MkDocs. This will enable them to be more easily
supported and updates outside MkDocs releases.

### Major Additions to Version 0.13.0

#### Search

Support for search has now been added to MkDocs. This is based on the
JavaScript library [lunr.js]. It has been added to both the `mkdocs` and
`readthedocs` themes. See the custom theme documentation on [supporting search]
for adding it to your own themes.

[lunr.js]: https://lunrjs.com/
[supporting search]: ../user-guide/styling-your-docs.md#search-and-themes

#### New Command Line Interface

The command line interface for MkDocs has been re-written with the Python
library [Click]. This means that MkDocs now has an easier to use interface
with better help output.

This change is partially backwards incompatible as while undocumented it was
possible to pass any configuration option to the different commands. Now only
a small subset of the configuration options can be passed to the commands. To
see in full commands and available arguments use `mkdocs --help` and
`mkdocs build --help` to have them displayed.

[Click]: http://click.pocoo.org/4/

#### Support Extra HTML and XML files

Like the [extra_javascript] and [extra_css] configuration options, a new
option named [extra_templates] has been added. This will automatically be
populated with any `.html` or `.xml` files in the project docs directory.

Users can place static HTML and XML files and they will be copied over, or they
can also use Jinja2 syntax and take advantage of the [global variables].

By default MkDocs will use this approach to create a sitemap for the
documentation.

[extra_javascript]: ../user-guide/configuration.md#extra_javascript
[extra_css]: ../user-guide/configuration.md#extra_css
[extra_templates]: ../user-guide/configuration.md#extra_templates
[global variables]: ../user-guide/styling-your-docs.md#global-context

### Other Changes and Additions to Version 0.13.0

* Add support for [Markdown extension configuration options]. (#435)
* MkDocs now ships Python [wheels]. (#486)
* Only include the build date and MkDocs version on the homepage. (#490)
* Generate sitemaps for documentation builds. (#436)
* Add a clearer way to define nested pages in the configuration. (#482)
* Add an [extra config] option for passing arbitrary variables to the template. (#510)
* Add `--no-livereload` to `mkdocs serve` for a simpler development server. (#511)
* Add copyright display support to all themes (#549)
* Add support for custom commit messages in a `mkdocs gh-deploy` (#516)
* Bugfix: Fix linking to media within the same directory as a markdown file
  called index.md (#535)
* Bugfix: Fix errors with Unicode filenames (#542).

[extra config]: ../user-guide/configuration.md#extra
[Markdown extension configuration options]: ../user-guide/configuration.md#markdown_extensions
[wheels]: https://pythonwheels.com/

## Version 0.12.2 (2015-04-22)

* Bugfix: Fix a regression where there would be an error if some child titles
  were missing but others were provided in the pages config. (#464)

## Version 0.12.1 (2015-04-14)

* Bugfix: Fixed a CSS bug in the table of contents on some browsers where the
  bottom item was not clickable.

## Version 0.12.0 (2015-04-14)

* Display the current MkDocs version in the CLI output. (#258)
* Check for CNAME file when using gh-deploy. (#285)
* Add the homepage back to the navigation on all themes. (#271)
* Add a strict more for local link checking. (#279)
* Add Google analytics support to all themes. (#333)
* Add build date and MkDocs version to the ReadTheDocs and MkDocs theme
  outputs. (#382)
* Standardize highlighting across all themes and add missing languages. (#387)
* Add a verbose flag. (-v) to show more details about what the build. (#147)
* Add the option to specify a remote branch when deploying to GitHub. This
  enables deploying to GitHub pages on personal and repo sites. (#354)
* Add favicon support to the ReadTheDocs theme HTML. (#422)
* Automatically refresh the browser when files are edited. (#163)
* Bugfix: Never re-write URLs in code blocks. (#240)
* Bugfix: Don't copy ditfiles when copying media from the `docs_dir`. (#254)
* Bugfix: Fix the rendering of tables in the ReadTheDocs theme. (#106)
* Bugfix: Add padding to the bottom of all bootstrap themes. (#255)
* Bugfix: Fix issues with nested Markdown pages and the automatic pages
  configuration. (#276)
* Bugfix: Fix a URL parsing error with GitHub enterprise. (#284)
* Bugfix: Don't error if the mkdocs.yml is completely empty. (#288)
* Bugfix: Fix a number of problems with relative URLs and Markdown files. (#292)
* Bugfix: Don't stop the build if a page can't be found, continue with other
  pages. (#150)
* Bugfix: Remove the site_name from the page title, this needs to be added
  manually. (#299)
* Bugfix: Fix an issue with table of contents cutting off Markdown. (#294)
* Bugfix: Fix hostname for BitBucket. (#339)
* Bugfix: Ensure all links end with a slash. (#344)
* Bugfix: Fix repo links in the readthedocs theme. (#365)
* Bugfix: Include jQuery locally to avoid problems using MkDocs offline. (#143)
* Bugfix: Don't allow the docs_dir to be in the site_dir or vice versa. (#384)
* Bugfix: Remove inline CSS in the ReadTheDocs theme. (#393)
* Bugfix: Fix problems with the child titles due to the order the pages config
  was processed. (#395)
* Bugfix: Don't error during live reload when the theme doesn't exist. (#373)
* Bugfix: Fix problems with the Meta extension when it may not exist. (#398)
* Bugfix: Wrap long inline code otherwise they will run off the screen. (#313)
* Bugfix: Remove HTML parsing regular expressions and parse with HTMLParser to
  fix problems with titles containing code. (#367)
* Bugfix: Fix an issue with the scroll to anchor causing the title to be hidden
  under the navigation. (#7)
* Bugfix: Add nicer CSS classes to the HTML tables in bootswatch themes. (#295)
* Bugfix: Fix an error when passing in a specific config file with
  `mkdocs serve`. (#341)
* Bugfix: Don't overwrite index.md files with the `mkdocs new` command. (#412)
* Bugfix: Remove bold and italic from code in the ReadTheDocs theme. (#411)
* Bugfix: Display images inline in the MkDocs theme. (#415)
* Bugfix: Fix problems with no-highlight in the ReadTheDocs theme. (#319)
* Bugfix: Don't delete hidden files when using `mkdocs build --clean`. (#346)
* Bugfix: Don't block newer versions of Python-markdown on Python >= 2.7. (#376)
* Bugfix: Fix encoding issues when opening files across platforms. (#428)

## Version 0.11.1 (2014-11-20)

* Bugfix: Fix a CSS wrapping issue with code highlighting in the ReadTheDocs
  theme. (#233)

## Version 0.11.0 (2014-11-18)

* Render 404.html files if they exist for the current theme. (#194)
* Bugfix: Fix long nav bars, table rendering and code highlighting in MkDocs
  and ReadTheDocs themes. (#225)
* Bugfix: Fix an issue with the google_analytics code. (#219)
* Bugfix: Remove `__pycache__` from the package tar. (#196)
* Bugfix: Fix markdown links that go to an anchor on the current page. (#197)
* Bugfix: Don't add `prettyprint well` CSS classes to all HTML, only add it in
  the MkDocs theme. (#183)
* Bugfix: Display section titles in the ReadTheDocs theme. (#175)
* Bugfix: Use the polling observer in watchdog so rebuilding works on
  filesystems without inotify. (#184)
* Bugfix: Improve error output for common configuration related errors. (#176)

## Version 0.10.0 (2014-10-29)

* Added support for Python 3.3 and 3.4. (#103)
* Configurable Python-Markdown extensions with the config setting
  `markdown_extensions`. (#74)
* Added `mkdocs json` command to output your rendered
  documentation as json files. (#128)
* Added `--clean` switch to `build`, `json` and `gh-deploy` commands to
  remove stale files from the output directory. (#157)
* Support multiple theme directories to allow replacement of
  individual templates rather than copying the full theme. (#129)
* Bugfix: Fix `<ul>` rendering in readthedocs theme. (#171)
* Bugfix: Improve the readthedocs theme on smaller displays. (#168)
* Bugfix: Relaxed required python package versions to avoid clashes. (#104)
* Bugfix: Fix issue rendering the table of contents with some configs. (#146)
* Bugfix: Fix path for embedded images in sub pages. (#138)
* Bugfix: Fix `use_directory_urls` config behavior. (#63)
* Bugfix: Support `extra_javascript` and `extra_css` in all themes. (#90)
* Bugfix: Fix path-handling under Windows. (#121)
* Bugfix: Fix the menu generation in the readthedocs theme. (#110)
* Bugfix: Fix the mkdocs command creation under Windows. (#122)
* Bugfix: Correctly handle external `extra_javascript` and `extra_css`. (#92)
* Bugfix: Fixed favicon support. (#87)
