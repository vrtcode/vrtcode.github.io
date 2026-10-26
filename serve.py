#!/usr/bin/env python3
"""Loopback-only static preview, with the site's 404 page and optional Pages subpath."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class Handler(SimpleHTTPRequestHandler):
    base_path = ''

    def do_GET(self):
        path = urlsplit(self.path).path
        if self.base_path:
            if path == self.base_path:
                self.send_response(301)
                self.send_header('Location', self.base_path + '/')
                self.end_headers()
                return
            if not path.startswith(self.base_path + '/'):
                self.send_error(404)
                return
            self.path = self.path[len(self.base_path):]
        super().do_GET()

    def do_HEAD(self):
        path = urlsplit(self.path).path
        if self.base_path:
            if not path.startswith(self.base_path + '/'):
                self.send_error(404)
                return
            self.path = self.path[len(self.base_path):]
        super().do_HEAD()

    def send_error(self, code, message=None, explain=None):
        page = Path(self.directory) / '404.html'
        if code != 404 or not page.is_file():
            return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent / 'dist')
    parser.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    if not (args.directory / 'index.html').is_file():
        parser.error('Build the website first: python3 build.py')
    manifest = json.loads((args.directory / 'build-manifest.json').read_text())
    Handler.base_path = manifest['base_path']
    handler = partial(Handler, directory=str(args.directory.resolve()))
    print(f'Preview: http://127.0.0.1:{args.port}{Handler.base_path}/', flush=True)
    try:
        ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
