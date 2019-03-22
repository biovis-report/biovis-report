# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import logging
from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


log = logging.getLogger(__name__)
base_path = os.path.dirname(os.path.abspath(__file__))


class HeaderInjectorPlugin(BasePlugin):
    """ Add a js list into MkDocs html header. """

    config_scheme = (
        ('extra_header_js', config_options.Type(list)),
    )

    def on_post_page(self, output, page, config, **kwargs):
        "Inject extra javascript into html header."
        soup = BeautifulSoup(output, 'html.parser')
        head = soup.find('head')
        for js in self.config['extra_header_js']:
            script = soup.new_tag('script')
            script['src'] = js
            script['type'] = 'application/javascript'
            # script['defer'] = None
            head.insert(-1, script)

        log.debug('Inject js list into header: %s' % str(self.config['extra_header_js']))
        return str(soup)
