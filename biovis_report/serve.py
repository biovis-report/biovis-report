import os
import logging
import shutil
import tempfile
import posixpath
import io
import wsgiref
import re
import cgi
from urllib.parse import urlsplit
from os.path import isdir, isfile, join

import jinja2.exceptions

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort
from mkdocs.livereload import LiveReloadServer

log = logging.getLogger(__name__)


class CustomLiveReloadServer(LiveReloadServer):
    def __init__(self, builder, host, port, root, mount_path="/", polling_interval=0.5, shutdown_delay=0.25, **kwargs):
        super().__init__(builder, host, port, root, mount_path, polling_interval, shutdown_delay, **kwargs)

    def _serve_request(self, environ, start_response):
        # https://bugs.python.org/issue16679
        # https://github.com/bottlepy/bottle/blob/f9b1849db4/bottle.py#L984
        path = environ["PATH_INFO"].encode("latin-1").decode("utf-8", "ignore")

        method = environ["REQUEST_METHOD"]
        if method == 'PUT' and re.match(r'.*.md$', path):
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            file_obj = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'], keep_blank_values=True)
            file_content = file_obj.getvalue('markdown')
            file_path = os.path.join(self.root, path.lstrip('/'))
            # print(path, file_path, file_content)
            if os.path.isfile(file_path) and file_content:
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                    start_response("204 No Content", [])
                    return []
            else:
                return None

        if path.startswith("/livereload/"):
            m = re.fullmatch(r"/livereload/([0-9]+)/[0-9]+", path)
            if m:
                epoch = int(m[1])
                start_response("200 OK", [("Content-Type", "text/plain")])

                def condition():
                    return self._visible_epoch > epoch

                with self._epoch_cond:
                    if not condition():
                        # Stall the browser, respond as soon as there's something new.
                        # If there's not, respond anyway after a minute.
                        self._log_poll_request(environ.get("HTTP_REFERER"), request_id=path)
                        self._epoch_cond.wait_for(condition, timeout=self.poll_response_timeout)
                    return [b"%d" % self._visible_epoch]

        if path.startswith(self.mount_path):
            rel_file_path = path[len(self.mount_path):]

            if path.endswith("/"):
                rel_file_path += "index.html"
            # Prevent directory traversal - normalize the path.
            rel_file_path = posixpath.normpath("/" + rel_file_path).lstrip("/")
            file_path = os.path.join(self.root, rel_file_path)
        elif path == "/":
            start_response("302 Found", [("Location", self.mount_path)])
            return []
        else:
            return None  # Not found

        # Wait until the ongoing rebuild (if any) finishes, so we're not serving a half-built site.
        with self._epoch_cond:
            self._epoch_cond.wait_for(lambda: self._visible_epoch == self._wanted_epoch)
            epoch = self._visible_epoch

        try:
            file = open(file_path, "rb")
        except OSError:
            if not path.endswith("/") and os.path.isfile(os.path.join(file_path, "index.html")):
                start_response("302 Found", [("Location", path + "/")])
                return []
            return None  # Not found

        if self._watched_paths and file_path.endswith(".html"):
            with file:
                content = file.read()
            content = self._inject_js_into_html(content, epoch)
            file = io.BytesIO(content)
            content_length = len(content)
        else:
            content_length = os.path.getsize(file_path)

        content_type = self._guess_type(file_path)
        start_response(
            "200 OK", [("Content-Type", content_type), ("Content-Length", str(content_length))]
        )
        return wsgiref.util.FileWrapper(file)


def serve(config_file=None, dev_addr=None, strict=None, theme=None, site_dir=None,
          theme_dir=None, livereload='livereload', watch_theme=False, watch=[], **kwargs):
    """
    Start the MkDocs development server

    By default it will serve the documentation on http://localhost:8000/ and
    it will rebuild the documentation and refresh the page automatically
    whenever a file is edited.
    """

    # Create a temporary build directory, and set some options to serve it
    # PY2 returns a byte string by default. The Unicode prefix ensures a Unicode
    # string is returned. And it makes MkDocs temp dirs easier to identify.
    if site_dir is None:
        site_dir = tempfile.mkdtemp(prefix='mkdocs_')

    def mount_path(config):
        return urlsplit(config['site_url'] or '/').path

    def builder():
        log.info("Building documentation...")
        config = load_config(
            config_file=config_file,
            dev_addr=dev_addr,
            strict=strict,
            theme=theme,
            theme_dir=theme_dir,
            site_dir=site_dir,
            **kwargs
        )

        # ln -s <docs_dir> <site_dir>/markdown, for editing markdown file.
        # docs_dir is not root directory, so we need to link it to site_dir.
        markdown_link = os.path.join(site_dir, 'markdown')
        docs_dir = config['docs_dir']
        if os.path.realpath(markdown_link) == docs_dir:
            pass
        else:
            # Maybe the site_dir doesn't exist.
            # It will cause mkdocs.exceptions.Abort: FileNotFoundError: [Errno 2] No such file or directory
            if not os.path.isdir(site_dir):
                os.makedirs(site_dir)
            os.symlink(docs_dir, markdown_link)

        # combine CLI watch arguments with config file values
        if config["watch"] is None:
            config["watch"] = watch
        else:
            config["watch"].extend(watch)

        # Override a few config settings after validation
        config['site_url'] = 'http://{}{}'.format(config['dev_addr'], mount_path(config))

        live_server = livereload in ['dirty', 'livereload']
        dirty = livereload == 'dirty'
        build(config, live_server=live_server, dirty=dirty)
        return config

    try:
        # Perform the initial build
        config = builder()

        host, port = config['dev_addr']
        server = CustomLiveReloadServer(builder=builder, host=host, port=port, root=site_dir, mount_path=mount_path(config))

        def error_handler(code):
            if code in (404, 500):
                error_page = join(site_dir, f'{code}.html')
                if isfile(error_page):
                    with open(error_page, 'rb') as f:
                        return f.read()

        server.error_handler = error_handler

        if livereload in ['livereload', 'dirty']:
            # Watch the documentation files, the config file and the theme files.
            server.watch(config['docs_dir'])
            server.watch(config['config_file_path'])

            if watch_theme:
                for d in config['theme'].dirs:
                    server.watch(d)

            # Run `serve` plugin events.
            server = config['plugins'].run_event('serve', server, config=config, builder=builder)

            for item in config['watch']:
                server.watch(item)

        try:
            server.serve()
        except KeyboardInterrupt:
            log.info("Shutting down...")
        finally:
            server.shutdown()
    except jinja2.exceptions.TemplateError:
        # This is a subclass of OSError, but shouldn't be suppressed.
        raise
    except OSError as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise Abort(f'{type(e).__name__}: {e}')
    finally:
        if isdir(site_dir):
            shutil.rmtree(site_dir)
