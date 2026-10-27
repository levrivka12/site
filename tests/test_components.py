import re
import unittest

from site_base import (
    ALL_PAGES,
    HOME,
    ROOT,
    SiteTestCase,
    read_text,
)

FORM_PAGES = [HOME, 'contact.html']
CCSS = (ROOT / 'css/modern-business.css').read_text(encoding='utf-8')
SITE_JS = (ROOT / 'js/site.js').read_text(encoding='utf-8')
FORM_JS = (ROOT / 'js/form-submission-handler.js').read_text(encoding='utf-8')


class FormTests(SiteTestCase):
    def test_forms_have_https_action_and_gform_class(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                forms = root.findall('.//form')
                self.assertGreaterEqual(len(forms), 1, f'{p} missing form')
                for f in forms:
                    action = f.get('action') or ''
                    self.assertTrue(action.startswith('https://'), f'{p}: form action not https')
                    self.assertIn('gform', (f.get('class') or ''), f'{p}: form missing gform class')
                    self.assertEqual((f.get('method') or 'POST').upper(), 'POST')

    def test_forms_use_native_validation(self):
        for p in FORM_PAGES:
            src = self.get_source(p)
            self.assertNotIn('novalidate', src, f'{p} must use native validation (no novalidate)')

    def test_labels_paired_with_inputs(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                for label in root.findall('.//label'):
                    target = label.get('for')
                    if target:
                        self.assertTrue(
                            root.find(f'.//*[@id="{target}"]') is not None,
                            f'{p}: label for="{target}" has no matching input')

    def test_required_fields_semantics(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                for name in ['name', 'phone', 'email', 'message']:
                    fields = root.findall(f'.//input[@name="{name}"]') + root.findall(f'.//textarea[@name="{name}"]')
                    self.assertEqual(len(fields), 1, f'{p}: field {name} count')
                    self.assertIsNotNone(fields[0].get('required'), f'{p}: {name} must be required')

    def test_consent_checkbox_required_with_privacy_link(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                consent = root.findall('.//input[@id="consent"]')
                self.assertEqual(len(consent), 1, f'{p} missing consent checkbox')
                self.assertIsNotNone(consent[0].get('required'), f'{p}: consent must be required')
                container = consent[0].getparent()
                text = ''.join(container.itertext())
                self.assertIn('רבקה לב', text)
                self.assertIn('privacy-policy.html', ''.join(a.get('href') or '' for a in container.findall('.//a')))

    def test_honeypot_hidden_and_inert(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                honeypot = root.findall('.//textarea[@name="notUsed"]') + root.findall('.//input[@name="notUsed"]')
                self.assertEqual(len(honeypot), 1, f'{p} missing honeypot')
                hp = honeypot[0]
                self.assertEqual(hp.get('tabindex'), '-1', f'{p}: honeypot must have tabindex=-1')
                ancestors = hp.iterancestors()
                self.assertTrue(
                    any('d-none' in (anc.get('class') or '') for anc in ancestors),
                    f'{p}: honeypot must be visually hidden via d-none wrapper')

    def test_success_and_failure_messages(self):
        for p in FORM_PAGES:
            with self.subTest(page=p):
                root = self.get_page(p)
                ok = root.findall('.//div[@class="thankyou_message d-none"]')
                self.assertEqual(len(ok), 1, f'{p} missing thankyou_message')
                self.assertEqual(ok[0].get('role'), 'status')
                self.assertIsNotNone(ok[0].get('tabindex'), f'{p}: thankyou_message not focusable')
                bad = root.findall('.//div[@class="failure_message d-none"]')
                self.assertEqual(len(bad), 1, f'{p} missing failure_message')
                self.assertEqual(bad[0].get('role'), 'alert')
                self.assertIsNotNone(bad[0].get('tabindex'), f'{p}: failure_message not focusable')

    def test_form_handler_bindings(self):
        self.assertIn("document.querySelectorAll(\"form.gform\")", FORM_JS)
        self.assertIn('form.action', FORM_JS)
        self.assertIn('application/x-www-form-urlencoded', FORM_JS)
        self.assertIn('".failure_message"', FORM_JS)
        self.assertIn('".thankyou_message"', FORM_JS)
        self.assertIn('setCustomValidity', FORM_JS)
        self.assertIn('hebrewValidityMessage', FORM_JS)
        self.assertIn('"invalid"', FORM_JS)
        self.assertNotIn('console.log', FORM_JS)


class EmbeddedContentTests(SiteTestCase):
    def test_all_video_iframes_are_youtube_with_titles(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            iframes = root.findall('.//iframe')
            for f in iframes:
                frame_id = f.get('id') or ''
                embed = (f.get('src') or f.get('data-src') or '')
                if frame_id == 'clinicMap' or 'maps.google.com' in embed:
                    continue  # click-to-load Google map, not a video
                with self.subTest(page=p, src=embed[:80]):
                    # Regular youtube.com domain: youtube-nocookie.com triggers
                    # YouTube's "Error 153: video player configuration error"
                    # in the late-2025 embed enforcement, so it must not be used.
                    self.assertIn('youtube.com/embed/', embed,
                                  f'{p}: video iframe must embed youtube.com (found {embed[:60]})')
                    self.assertNotIn('youtube-nocookie.com', embed,
                                     f'{p}: youtube-nocookie embeds trigger error 153 (found {embed[:60]})')
                    self.assertTrue((f.get('title') or '').strip(), f'{p}: iframe missing title attr')
                    # YouTube's late-2025 embed enforcement rejects requests without an
                    # identifying Referer; keep the policy explicit on every video frame.
                    self.assertEqual(f.get('referrerpolicy'), 'strict-origin-when-cross-origin',
                                     f'{p}: youtube iframe missing referrerpolicy attr (error 153 fix)')

    def test_map_is_click_to_load(self):
        root = self.get_page('contact.html')
        self.assertIsNotNone(root.find('.//*[@id="mapPlaceholder"]'), 'contact.html missing #mapPlaceholder')
        self.assertIsNotNone(root.find('.//*[@id="clinicMapBtn"]'), 'contact.html missing #clinicMapBtn')
        map_frame = root.find('.//iframe[@data-src]')
        self.assertIsNotNone(map_frame, 'contact.html: map iframe should use data-src for click-to-load')
        self.assertIn('maps.google.com', map_frame.get('data-src'))

    def test_no_autoplay_youtube(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for src in root.findall('.//iframe'):
                embed = (src.get('src') or src.get('data-src') or '')
                self.assertNotIn('autoplay=1', embed, f'{p}: embed {embed[:60]} must not autoplay')

    def test_external_links_open_safely(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for a in root.findall('.//a'):
                href = a.get('href') or ''
                if href.startswith('http') and 'rivkalev.com' not in href and 'script.google.com' not in href:
                    with self.subTest(page=p, href=href):
                        self.assertEqual(a.get('target'), '_blank', f'{p}: external anchor {href} without target=_blank')
                        self.assertEqual(a.get('rel'), 'noopener', f'{p}: external anchor {href} without rel=noopener')


class A11ySupportTests(SiteTestCase):
    def test_css_has_skip_link_rules(self):
        self.assertIn('.skip-link', CCSS)
        self.assertTrue('position: absolute' in CCSS or 'position:absolute' in CCSS)

    def test_css_has_reduced_motion_block(self):
        self.assertIn('prefers-reduced-motion', CCSS)

    def test_css_has_cookie_banner_rules(self):
        self.assertIn('.cookie-banner', CCSS)

    def test_css_has_carousel_pause_button_styles(self):
        self.assertIn('.carousel-pause-btn', CCSS)
        self.assertIn('position: absolute', CCSS)
        self.assertIn('opacity', CCSS)

    def test_site_js_uses_localstorage_flag(self):
        self.assertIn('cookieNoticeDismissed', SITE_JS)
        self.assertIn('cookieAccept', SITE_JS)
        self.assertIn('cookieNotice', SITE_JS)

    def test_focus_visible_outlines(self):
        self.assertIn(':focus-visible', CCSS)

    def test_whatsapp_group_links(self):
        for p in ALL_PAGES:
            root = self.get_page(p)
            for a in root.findall('.//a'):
                href = a.get('href') or ''
                with self.subTest(page=p, href=href):
                    if 'chat.whatsapp.com' in href:
                        self.assertEqual(a.get('rel'), 'noopener')
                        self.assertEqual(a.get('target'), '_blank')


if __name__ == '__main__':
    unittest.main()
