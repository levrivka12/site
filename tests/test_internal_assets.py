import re
import unittest

from site_base import ALL_PAGES, ROOT, SiteTestCase, collect_all_ids, is_local_link, local_href_target

EXTERNAL_PREFIXES = ('mailto:', 'tel:', 'javascript:', 'data:', 'http://', 'https://')


class InternalLinksTests(SiteTestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_ids = collect_all_ids()

    def _assert_target_exists(self, page, path, fragment):
        if path is not None:
            target = ROOT / path
            self.assertTrue(target.exists(), f'{page}: broken link to {path}')
        if fragment:
            self.assertIn(fragment, self.all_ids, f'{page}: missing anchor #{fragment}')

    def test_all_local_hrefs_resolve(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for a in root.findall('.//a'):
                href = a.get('href')
                if not is_local_link(href):
                    continue
                with self.subTest(page=p, href=href):
                    if href == '#':
                        continue
                    path, fragment = local_href_target(href)
                    self._assert_target_exists(p, path, fragment)

    def test_all_local_img_srcs_resolve(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for img in root.findall('.//img'):
                with self.subTest(page=p, img=img.get('src')):
                    src = img.get('src')
                    self.assertTrue(src, f'{p}: img without src')
                    if src.startswith(EXTERNAL_PREFIXES):
                        continue
                    self.assertTrue((ROOT / src.split('#')[0]).exists(), f'{p}: missing image {src}')

    def test_local_favicon_present_on_disk(self):
        self.assertTrue((ROOT / 'res/favicon.svg').is_file())

    def test_all_script_srcs_resolve(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for s in root.findall('.//script'):
                src = s.get('src')
                if not src or src.startswith(EXTERNAL_PREFIXES):
                    continue
                with self.subTest(page=p, src=src):
                    self.assertTrue((ROOT / src).exists(), f'{p}: missing script {src}')

    def test_local_css_and_icons_resolved(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for l in root.findall('.//link'):
                href = l.get('href')
                if not href or href.startswith(EXTERNAL_PREFIXES):
                    continue
                with self.subTest(page=p, href=href):
                    self.assertTrue((ROOT / href).exists(), f'{p}: missing link target {href}')

    def test_inline_style_urls_resolve(self):
        pattern = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")
        for p in ALL_PAGES:
            src = self.get_source(p)
            for m in pattern.finditer(src):
                url = m.group(1)
                with self.subTest(page=p, style_url=url):
                    if url.startswith(EXTERNAL_PREFIXES):
                        continue
                    candidate = ROOT / url
                    if not candidate.is_file():
                        note = f'{p}: style url not on disk: {url} (checking under res/)'
                        fallback = ROOT / 'res' / url
                        self.assertTrue(fallback.is_file(), note)


if __name__ == '__main__':
    unittest.main()
