# MkDocs Plugins

A Guide to installing, using and creating MkDocs Plugins

---

## Installing Plugins

Before a plugin can be used, it must be installed on the system. If you are
using a plugin which comes with MkDocs, then it was installed when you installed
MkDocs. However, to install third party plugins, you need to determine the
appropriate package name and install it using `pip`:

    pip install mkdocs-foo-plugin

Once a plugin has been successfully installed, it is ready to use. It just needs
to be [enabled](#using-plugins) in the configuration file.

## Using Plugins

The [`plugins`][config] configuration option should contain a list of plugins to
use when building the site. Each "plugin" must be a string name assigned to the
plugin (see the documentation for a given plugin to determine its "name"). A
plugin listed here must already be [installed](#installing-plugins).

```yaml
plugins:
    - search
```

Some plugins may provide configuration options of their own. If you would like
to set any configuration options, then you can nest a key/value mapping
(`option_name: option value`) of any options that a given plugin supports. Note
that a colon (`:`) must follow the plugin name and then on a new line the option
name and value must be indented and separated by a colon. If you would like to
define multiple options for a single plugin, each option must be defined on a
separate line.

```yaml
plugins:
    - search:
        lang: en
        foo: bar
```

For information regarding the configuration options available for a given plugin,
see that plugin's documentation.

For a list of default plugins and how to override them, see the
[configuration][config] documentation.

## Developing Plugins

Like MkDocs, plugins must be written in Python. It is generally expected that
each plugin would be distributed as a separate Python module, although it is
possible to define multiple plugins in the same module. At a minimum, a MkDocs
Plugin must consist of a [BasePlugin] subclass and an [entry point] which
points to it.

### BasePlugin

A subclass of `mkdocs.plugins.BasePlugin` should define the behavior of the plugin.
The class generally consists of actions to perform on specific events in the build
process as well as a configuration scheme for the plugin.

All `BasePlugin` subclasses contain the following attributes:

#### config_scheme

:   A tuple of configuration validation instances. Each item must consist of a
    two item tuple in which the first item is the string name of the
    configuration option and the second item is an instance of
    `mkdocs.config.config_options.BaseConfigOption` or any of its subclasses.

    For example, the following `config_scheme` defines three configuration options: `foo`, which accepts a string; `bar`, which accepts an integer; and `baz`, which accepts a boolean value.

        class MyPlugin(mkdocs.plugins.BasePlugin):
            config_scheme = (
                ('foo', mkdocs.config.config_options.Type(mkdocs.utils.string_types, default='a default value')),
                ('bar', mkdocs.config.config_options.Type(int, default=0)),
                ('baz', mkdocs.config.config_options.Type(bool, default=True))
            )

    When the user's configuration is loaded, the above scheme will be used to
    validate the configuration and fill in any defaults for settings not
    provided by the user. The validation classes may be any of the classes
    provided in `mkdocs.config.config_options` or a third party subclass defined
    in the plugin.

    Any settings provided by the user which fail validation or are not defined
    in the `config_scheme` will raise a `mkdocs.config.base.ValidationError`.

#### config

:   A dictionary of configuration options for the plugin, which is populated by
    the `load_config` method after configuration validation has completed. Use
    this attribute to access options provided by the user.

        def on_pre_build(self, config):
            if self.config['bool_option']:
                # implement "bool_option" functionality here...

All `BasePlugin` subclasses contain the following method(s):

#### load_config(options)

:   Loads configuration from a dictionary of options. Returns a tuple of
    `(errors, warnings)`. This method is called by MkDocs during configuration
    validation and should not need to be called by the plugin.

#### on_&lt;event_name&gt;()

:   Optional methods which define the behavior for specific [events]. The plugin
    should define its behavior within these methods. Replace `<event_name>` with
    the actual name of the event. For example, the `pre_build` event would be
    defined in the `on_pre_build` method.

    Most events accept one positional argument and various keyword arguments. It
    is generally expected that the positional argument would be modified (or
    replaced) by the plugin and returned. If nothing is returned (the method
    returns `None`), then the original, unmodified object is used. The keyword
    arguments are simply provided to give context and/or supply data which may
    be used to determine how the positional argument should be modified. It is
    good practice to accept keyword arguments as `**kwargs`. In the event that
    additional keywords are provided to an event in a future version of MkDocs,
    there will be no need to alter your plugin.

    For example, the following event would add an additional static_template to
    the theme config:

        class MyPlugin(BasePlugin):
            def on_config(self, config, **kwargs):
                config['theme'].static_templates.add('my_template.html')
                return config

### Events

There are three kinds of events: [Global Events], [Page Events] and
[Template Events].

#### Global Events

Global events are called once per build at either the beginning or end of the
build process. Any changes made in these events will have a global effect on the
entire site.

##### on_serve

:   The `serve` event is only called when the `serve` command is used during
    development. It is passed the `Server` instance which can be modified before
    it is activated. For example, additional files or directories could be added
    to the list of "watched" files for auto-reloading.

    Parameters:
    : __server:__ `livereload.Server` instance
    : __config:__ global configuration object

    Returns:
    : `livereload.Server` instance

##### on_config

:   The `config` event is the first event called on build and is run immediately
    after the user configuration is loaded and validated. Any alterations to the
    config should be made here.

    Parameters:
    : __config:__ global configuration object

    Returns:
    : global configuration object

##### on_pre_build

:   The `pre_build` event does not alter any variables. Use this event to call
    pre-build scripts.

    Parameters:
    : __config:__ global configuration object

##### on_files

:   The `files` event is called after the files collection is populated from the
    `docs_dir`. Use this event to add, remove, or alter files in the
    collection. Note that Page objects have not yet been associated with the
    file objects in the collection. Use [Page Events] to manipulate page
    specific data.

    Parameters:
    : __files:__ global files collection
    : __config:__ global configuration object

    Returns:
    : global files collection

##### on_nav

:   The `nav` event is called after the site navigation is created and can
    be used to alter the site navigation.

    Parameters:
    : __nav:__ global navigation object
    : __config:__ global configuration object
    : __files:__ global files collection

    Returns:
    : global navigation object

##### on_env

:   The `env` event is called after the Jinja template environment is created
    and can be used to alter the Jinja environment.

    Parameters:
    : __env:__ global Jinja environment
    : __config:__ global configuration object
    : __files:__ global files collection

    Returns:
    : global Jinja Environment

##### on_post_build

:   The `post_build` event does not alter any variables. Use this event to call
    post-build scripts.

    Parameters:
    : __config:__ global configuration object

#### Template Events

Template events are called once for each non-page template. Each template event
will be called for each template defined in the [extra_templates] config setting
as well as any [static_templates] defined in the theme. All template events are
called after the [env] event and before any [page events].

##### on_pre_template

:   The `pre_template` event is called immediately after the subject template is
    loaded and can be used to alter the content of the template.

    Parameters:
    : __template__: the template contents as string
    : __template_name__: string filename of template
    : __config:__ global configuration object

    Returns:
    : template contents as string

##### on_template_context

:   The `template_context` event is called immediately after the context is created
    for the subject template and can be used to alter the context for that specific
    template only.

    Parameters:
    : __context__: dict of template context variables
    : __template_name__: string filename of template
    : __config:__ global configuration object

    Returns:
    : dict of template context variables

##### on_post_template

:   The `post_template` event is called after the template is rendered, but before
    it is written to disc and can be used to alter the output of the template.
    If an empty string is returned, the template is skipped and nothing is is
    written to disc.

    Parameters:
    : __output_content__: output of rendered template as string
    : __template_name__: string filename of template
    : __config:__ global configuration object

    Returns:
    : output of rendered template as string

#### Page Events

Page events are called once for each Markdown page included in the site. All
page events are called after the [post_template] event and before the
[post_build] event.

##### on_pre_page

:   The `pre_page` event is called before any actions are taken on the subject
    page and can be used to alter the `Page` instance.

    Parameters:
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object
    : __files:__ global files collection

    Returns:
    : `mkdocs.nav.Page` instance

##### on_page_read_source

:   The `on_page_read_source` event can replace the default mechanism to read
    the contents of a page's source from the filesystem.

    Parameters:
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object

    Returns:
    : The raw source for a page as unicode string. If `None` is returned, the
      default loading from a file will be performed.

##### on_page_markdown

:   The `page_markdown` event is called after the page's markdown is loaded
    from file and can be used to alter the Markdown source text. The meta-
    data has been stripped off and is available as `page.meta` at this point.

    Parameters:
    : __markdown:__ Markdown source text of page as string
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object
    : __files:__ global files collection

    Returns:
    : Markdown source text of page as string

##### on_page_content

:   The `page_content` event is called after the Markdown text is rendered to
    HTML (but before being passed to a template) and can be used to alter the
    HTML body of the page.

    Parameters:
    : __html:__ HTML rendered from Markdown source as string
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object
    : __files:__ global files collection

    Returns:
    : HTML rendered from Markdown source as string

##### on_page_context

:   The `page_context` event is called after the context for a page is created
    and can be used to alter the context for that specific page only.

    Parameters:
    : __context__: dict of template context variables
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object
    : __nav:__ global navigation object

    Returns:
    : dict of template context variables

##### on_post_page

:   The `post_page` event is called after the template is rendered, but
    before it is written to disc and can be used to alter the output of the
    page. If an empty string is returned, the page is skipped and nothing is
    written to disc.

    Parameters:
    : __output:__ output of rendered template as string
    : __page:__ `mkdocs.nav.Page` instance
    : __config:__ global configuration object

    Returns:
    : output of rendered template as string

### Entry Point

Plugins need to be packaged as Python libraries (distributed on PyPI separate
from MkDocs) and each must register as a Plugin via a setuptools entry_point.
Add the following to your `setup.py` script:

```python
entry_points={
    'mkdocs.plugins': [
        'pluginname = path.to.some_plugin:SomePluginClass',
    ]
}
```

The `pluginname` would be the name used by users (in the config file) and
`path.to.some_plugin:SomePluginClass` would be the importable plugin itself
(`from path.to.some_plugin import SomePluginClass`) where `SomePluginClass` is a
subclass of [BasePlugin] which defines the plugin behavior. Naturally, multiple
Plugin classes could exist in the same module. Simply define each as a separate
entry_point.

```python
entry_points={
    'mkdocs.plugins': [
        'featureA = path.to.my_plugins:PluginA',
        'featureB = path.to.my_plugins:PluginB'
    ]
}
```

Note that registering a plugin does not activate it. The user still needs to
tell MkDocs to use if via the config.

[BasePlugin]:#baseplugin
[config]: configuration.md#plugins
[entry point]: #entry-point
[env]: #on_env
[events]: #events
[extra_templates]: configuration.md#extra_templates
[Global Events]: #global-events
[Page Events]: #page-events
[post_build]: #on_post_build
[post_template]: #on_post_template
[static_templates]: configuration.md#static_templates
[Template Events]: #template-events
