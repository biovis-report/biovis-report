# -*- coding:utf-8 -*-
from __future__ import unicode_literals


class PluginRegistry:
    def __init__(self):
        self._internal_plugins = {}

    def register(self, plugin_class):
        self._internal_plugins.update({
            plugin_class.plugin_name: plugin_class
        })
        return self

    @property
    def internal_plugins(self):
        return self._internal_plugins


plugin_registry = PluginRegistry()

# For production
internal_plugins = plugin_registry.internal_plugins
