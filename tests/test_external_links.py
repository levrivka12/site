import unittest

from site_base import ALL_PAGES

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


def _network_available():
    try:
        return requests.get('https://example.com', timeout=10).status_code == 200
    except Exception:
        return False


TIMEOUT = 15


def status_ok(status):
    # any response below 500 counts as reachable; 404s on real links are failures
    return status < 500 and status != 404


def status_acceptable(status, url):
    if status >= 500:
        return False
    if status == 404:
        # some hosts return 404 for bot requests; treat these two hosts' 404s as soft-fail
        return False
    return True


@unittest.skipIf(requests is None, 'requests not available')
class ExternalLinksTests(unittest.TestCase):
    network_ok = False

    @classmethod
    def setUpClass(cls):
        cls.network_ok = _network_available()

    @unittest.skipUnless(_network_available(), 'network unavailable')
    def test_control_urls(self):
        self.assertEqual(requests.get('https://example.com', timeout=TIMEOUT).status_code, 200)

    def test_external_links_reachable(self):
        for p in ALL_PAGES:
            root = __import__('site_base').parse_page(p)
            urls = set()
            for a in root.findall('.//a'):
                href = a.get('href') or ''
                if href.startswith('http'):
                    urls.add(href.split('#')[0])
            for img in root.findall('.//img'):
                src = img.get('src') or ''
                if src.startswith('http'):
                    urls.add(src.split('#')[0])
            for s in root.findall('.//script'):
                src = s.get('src') or ''
                if src.startswith('http'):
                    urls.add(src.split('#')[0])
            for l in root.findall('.//link'):
                href = l.get('href') or ''
                if href.startswith('http'):
                    urls.add(href.split('#')[0])
            for url in sorted(urls):
                with self.subTest(page=p, url=url):
                    try:
                        resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
                    except requests.RequestException as err:
                        self.fail(f'{p}: unreachable external URL {url}: {err.__class__.__name__}')
                    self.assertTrue(
                        status_acceptable(resp.status_code, url),
                        f'{p}: external URL {url} returned {resp.status_code}')


if __name__ == '__main__':
    unittest.main()
