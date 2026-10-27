import http.server
import os
import socketserver
import threading
import unittest

import requests

from site_base import ALL_PAGES, ROOT

_MISSING = 'this-page-does-not-exist-9x8y.html'


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        pass


class HttpSmokeTests(unittest.TestCase):
    httpd = None
    port = None

    @classmethod
    def setUpClass(cls):
        handler = _QuietHandler
        handler.extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
        handler.extensions_map.update({
            '.html': 'text/html; charset=utf-8',
            '.js': 'text/javascript; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.svg': 'image/svg+xml',
        })
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        cls.httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
        cls.port = cls.httpd.server_address[1]
        cls._old_cwd = os.getcwd()
        os.chdir(ROOT)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        os.chdir(cls._old_cwd)

    def _get(self, path):
        return requests.get(f'http://127.0.0.1:{self.port}/{path}', timeout=10)

    def test_every_page_served(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                resp = self._get(p)
                self.assertEqual(resp.status_code, 200, f'{p} must serve HTTP 200')
                self.assertIn('text/html', resp.headers.get('Content-Type', ''))
                self.assertTrue(resp.content.strip().startswith(b'<!DOCTYPE html>'))

    def test_missing_page_returns_404(self):
        resp = self._get(_MISSING)
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
