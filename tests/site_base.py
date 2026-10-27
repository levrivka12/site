import pathlib
import unittest
from urllib.parse import unquote

from lxml import etree

ROOT = pathlib.Path(__file__).resolve().parent.parent

HOME = 'index.html'
CONTENT_PAGES = [
    'pediatric_physical_therapy.html',
    'pelvic_floor_rehabilitation.html',
    'pediatric_pelvic_floor.html',
    'lectures.html',
    'sadnaot.html',
    'movies.html',
    'posts.html',
    'tips.html',
    'reviews.html',
    'contact.html',
]
LEGAL_PAGES = [
    'privacy-policy.html',
    'terms-of-use.html',
    'accessibility-statement.html',
]
ERROR_PAGES = ['404.html']
OTHER_PAGES = LEGAL_PAGES + ERROR_PAGES

ALL_PAGES = [HOME] + CONTENT_PAGES + OTHER_PAGES

RETIREMENT_LEFTOVERS = [
    'placehold.it',
    'articles.html',
    'callButton1',
    'scollable',
    'jqBootstrapValidation',
    'mapouter',
    'nordvpn',
    'data-validation-required-message',
    'novalidate',
    'Toggle navigation',
    'contact_me.php',
]

EXPECTED_TITLES = {
    'index.html': 'רבקה לב - פיזיותרפיה התפתחותית, הדרכת הורים ושיקום רצפת אגן',
    'pediatric_physical_therapy.html': 'פיזיותרפיה התפתחותית לתינוקות וילדים - רבקה לב',
    'pelvic_floor_rehabilitation.html': 'שיקום רצפת אגן לנשים - רבקה לב',
    'pediatric_pelvic_floor.html': 'רצפת אגן לילדים וגמילה מחיתולים - רבקה לב',
    'lectures.html': 'הרצאות להורים ולצוותים מקצועיים - רבקה לב',
    'sadnaot.html': 'סדנאות לליווי התפתחותי ועיסוי תינוקות - רבקה לב',
    'movies.html': 'סרטוני הדרכה ותמיכה - רבקה לב',
    'posts.html': 'פוסטים, מאמרים ורעיונות להורים - רבקה לב',
    'tips.html': 'טיפים להורים ולמשפחות - רבקה לב',
    'reviews.html': 'המלצות ומשובים - רבקה לב',
    'contact.html': 'צור קשר - רבקה לב',
    'privacy-policy.html': 'מדיניות פרטיות ועוגיות - רבקה לב',
    'terms-of-use.html': 'תנאי שימוש באתר - רבקה לב',
    'accessibility-statement.html': 'הצהרת נגישות - רבקה לב',
    '404.html': 'העמוד לא נמצא - רבקה לב',
}

PARSER = etree.HTMLParser(recover=False, no_network=True)


def parse_page(name):
    raw = (ROOT / name).read_bytes()
    return etree.fromstring(raw, PARSER)


def read_text(name):
    return (ROOT / name).read_text(encoding='utf-8')


def is_local_link(url):
    if not url or url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'http://', 'https://')):
        return False
    return True


def local_href_target(url):
    path = unquote(url.split('#', 1)[0])
    fragment = url.split('#', 1)[1] if '#' in url else None
    if path == '':
        return (None, fragment)
    return (path, fragment)


def collect_all_ids():
    ids = set()
    for p in ALL_PAGES:
        root = parse_page(p)
        for element in root.iter():
            value = element.get('id')
            if value:
                ids.add(value)
                ids.add(unquote(value))
    return ids


class SiteTestCase(unittest.TestCase):
    """Base helper mixin."""

    @staticmethod
    def get_page(name):
        return parse_page(name)

    @staticmethod
    def get_source(name):
        return read_text(name)
