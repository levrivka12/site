import unittest

from site_base import (
    ALL_PAGES,
    CONTENT_PAGES,
    ERROR_PAGES,
    EXPECTED_TITLES,
    HOME,
    LEGAL_PAGES,
    RETIREMENT_LEFTOVERS,
    ROOT,
    SiteTestCase,
)

BREADCRUMB_PAGES = CONTENT_PAGES + LEGAL_PAGES
H1_FOR_PAGE = {
    'index.html': 'טיפול אישי',
    'contact.html': 'צור קשר',
    'pediatric_physical_therapy.html': 'פיזיותרפיה התפתחותית לתינוקות וילדים',
    'pelvic_floor_rehabilitation.html': 'שיקום רצפת אגן לנשים',
    'pediatric_pelvic_floor.html': 'רצפת אגן לילדים',
    'lectures.html': 'הרצאות',
    'sadnaot.html': 'סדנאות',
    'movies.html': 'סרטונים',
    'posts.html': 'פוסטים ומאמרים',
    'tips.html': 'טיפים',
    'reviews.html': 'המלצות',
    'privacy-policy.html': 'מדיניות פרטיות ועוגיות',
    'terms-of-use.html': 'תנאי שימוש באתר',
    'accessibility-statement.html': 'הצהרת נגישות',
    '404.html': 'הדף לא נמצא',
}


class StructureTests(SiteTestCase):
    def test_every_page_exists_and_parses_strictly(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                self.assertIsNotNone(root)

    def test_lang_is_hebrew_and_rtl(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                self.assertEqual(root.get('lang'), 'he')
                self.assertEqual(root.get('dir'), 'rtl')

    def test_css_overrides_bootstrap_ltr_text_align(self):
        css = (ROOT / 'css/modern-business.css').read_text(encoding='utf-8')
        self.assertIn('html[dir="rtl"] body', css)
        self.assertIn('text-align: right', css)
        self.assertIn('html[dir="rtl"] .form-check', css)
        self.assertIn('html[dir="rtl"] .form-check-input', css)

    def test_one_single_h1_per_page(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                h1s = root.findall('.//h1')
                self.assertEqual(len(h1s), 1, f'{p} must have exactly one h1')

    def test_h1_text_per_page(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                h1 = root.findall('.//h1')[0]
                text = ''.join(h1.itertext()).strip()
                text = ' '.join(text.split())
                self.assertIn(H1_FOR_PAGE[p], text, f'{p} h1 mismatch')

    def test_titles_are_unique_and_expected(self):
        titles = []
        for p in ALL_PAGES:
            root = self.get_page(p)
            title = root.findall('.//title')
            self.assertTrue(title, f'{p} missing title')
            titles.append(title[0].text)
            self.assertEqual(title[0].text, EXPECTED_TITLES[p], f'{p} title mismatch')
        self.assertEqual(len(titles), len(set(titles)), 'titles must be unique')

    def test_every_page_has_single_main(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                mains = root.findall('.//main')
                self.assertEqual(len(mains), 1, f'{p} must wrap content in one <main>')
                self.assertEqual(mains[0].get('id'), 'main')

    def test_navigation_aria_label(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                navs = root.findall('.//nav[@aria-label="תפריט ראשי"]')
                self.assertEqual(len(navs), 1, f'{p} missing primary nav with aria-label')

    def test_skip_link_present_and_targets_main(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                body = root.findall('.//body')[0]
                first_anchor = body.find('.//a[@class="skip-link"]')
                self.assertIsNotNone(first_anchor, f'{p} missing skip link')
                self.assertEqual(first_anchor.get('href'), '#main')

    def test_meta_description_non_empty(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                desc = root.findall('.//meta[@name="description"]')
                self.assertEqual(len(desc), 1, f'{p} needs one meta description')
                self.assertGreater(len((desc[0].get('content') or '').strip()), 20)

    def test_ga_snippet_anonymized(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                src = self.get_source(p)
                self.assertIn("gtag('config', 'UA-179818286-1', { anonymize_ip: true });", src)

    def test_favicon_and_theme_color(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                icons = root.findall('.//link[@rel="icon"]')
                self.assertTrue(icons, f'{p} missing favicon')
                theme = root.findall('.//meta[@name="theme-color"]')
                self.assertTrue(theme, f'{p} missing theme-color')

    def test_footer_rendered_on_every_page(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                footers = [f for f in root.findall('.//footer') if f.get('class') == 'py-5 bg-dark']
                self.assertEqual(len(footers), 1, f'{p} must have one footer')
                copyright_text = ''.join(footers[0].itertext())
                self.assertIn('כל הזכויות שמורות', copyright_text)

    def test_cookie_notice_and_site_js(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                notice = root.findall('.//div[@id="cookieNotice"]')
                self.assertTrue(notice, f'{p} missing cookieNotice div')
                accept = root.findall('.//button[@id="cookieAccept"]')
                self.assertTrue(accept, f'{p} missing cookieAccept button')
                srcs = [s.get('src') for s in root.findall('.//script') if s.get('src')]
                self.assertIn('js/site.js', srcs, f'{p} missing site.js script')

    def test_no_template_leftovers_anywhere(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                src = self.get_source(p)
                for token in RETIREMENT_LEFTOVERS:
                    self.assertNotIn(token, src, f'{p} still contains leftover {token}')

    def test_bootstrap_css_is_minified(self):
        for p in ALL_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                css = [l.get('href') for l in root.findall('.//link[@rel="stylesheet"]') if l.get('href')]
                self.assertIn('vendor/bootstrap/css/bootstrap.min.css', css, f'{p} must use minified bootstrap css')
                self.assertNotIn('vendor/bootstrap/css/bootstrap.css', css)

    def test_breadcrumbs_on_content_and_legal_pages(self):
        for p in BREADCRUMB_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                crumb = root.findall('.//ol[@class="breadcrumb"]')
                self.assertEqual(len(crumb), 1, f'{p} missing breadcrumb')
                self.assertEqual(crumb[0].get('aria-label'), 'נתיב הגלישה')
                current = root.findall('.//li[@class="breadcrumb-item active"][@aria-current="page"]')
                self.assertEqual(len(current), 1, f'{p} breadcrumb missing aria-current=current page')

    def test_no_breadcrumb_on_home_and_404(self):
        for p in [HOME] + ERROR_PAGES:
            root = self.get_page(p)
            self.assertEqual(len(root.findall('.//ol[@class="breadcrumb"]')), 0, f'{p} unexpected breadcrumb')

    def test_homepage_carousel_pause_button(self):
        root = self.get_page(HOME)
        buttons = [b for b in root.findall('.//button') if b.get('id') == 'carouselPause']
        self.assertEqual(len(buttons), 1, 'index needs #carouselPause toggle')
        btn = buttons[0]
        carousel = btn.getparent()
        self.assertEqual(carousel.get('id'), 'carouselExampleSlidesOnly',
                         'pause button must live inside the carousel')
        self.assertIsNotNone(btn.get('aria-label'))
        self.assertIn('התמונות', btn.get('aria-label'))
        self.assertIsNotNone(btn.get('aria-pressed'), 'pause button needs aria-pressed state')
        self.assertNotIn('btn', (btn.get('class') or '').split(),
                         'pause button must not be a styled .btn (it should be unobtrusive)')
        icon = btn.find('.//span')
        self.assertIsNotNone(icon, 'pause button needs an icon')
        self.assertIn('fa-pause', (icon.get('class') or ''))
        self.assertEqual(''.join(btn.itertext()).strip(), '',
                         'pause button must be icon-only; aria-label carries the name')

    def test_iccs_mention_on_home_and_pediatric_pelvic_floor(self):
        for p in [HOME, 'pediatric_pelvic_floor.html']:
            src = self.get_source(p)
            self.assertIn('ICCS', src, f'{p} missing ICCS mention')
        root = self.get_page('pediatric_pelvic_floor.html')
        iccs = [a for a in root.findall('.//a') if (a.get('href') or '').startswith('https://i-c-c-s.org')]
        self.assertTrue(iccs, 'pediatric_pelvic_floor must link ICCS site')


if __name__ == '__main__':
    unittest.main()
