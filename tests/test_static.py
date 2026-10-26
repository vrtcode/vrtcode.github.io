"""Read-only acceptance checks for the generated static portfolio."""
import os
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ.get('VRT_SITE', ROOT / 'dist'))
ENTRY = os.environ.get('VRT_ENTRY', 'index.html')
MANIFEST = SITE / 'build-manifest.json'
BASE = json.loads(MANIFEST.read_text()).get('base_path', '') if MANIFEST.is_file() else ''
SLUGS = ['android-integrity', 'realtime-security', 'worker-lifecycle',
         'mobile-sdk-analysis', 'push-integration-security',
         'network-observability', 'ios-attestation']


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class StaticSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (SITE / ENTRY).read_text()
        cls.doc = Document(cls.source)

    def test_english_document(self):
        self.assertIn(('html', {'lang': 'en'}), self.doc.tags)
        self.assertNotRegex(self.source, r'[\u0400-\u04ff]')

    def test_no_runtime_templates(self):
        self.assertNotIn('{{', self.source, 'Template bindings must be resolved at build time')
        self.assertNotIn('<x-dc', self.source)
        self.assertNotIn('<sc-', self.source)

    def test_only_local_scripts(self):
        for tag, attrs in self.doc.tags:
            if tag == 'script':
                self.assertTrue(attrs.get('src', '').startswith(BASE + '/assets/'))
                self.assertNotIn('support.js', attrs['src'])
        self.assertNotIn('text/x-dc', self.source)

    def test_no_external_render_dependencies(self):
        for tag, attrs in self.doc.tags:
            if tag in ('script', 'link', 'img', 'iframe', 'source'):
                for key in ('src', 'href'):
                    if key in attrs:
                        self.assertNotIn('fonts.googleapis.com', attrs[key])
                        self.assertNotIn('unpkg.com', attrs[key])

    def test_seven_real_case_pages(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                path = SITE / 'work' / slug / 'index.html'
                self.assertTrue(path.is_file(), f'Missing static page: {slug}')
                if path.is_file():
                    page = path.read_text()
                    self.assertIn('<h1', page)
                    self.assertNotIn('{{', page)
                    self.assertIn('og:image', page)
                    self.assertIn(slug, page)
        self.assertNotIn('#/work/', self.source)

    def test_complete_publication_assets(self):
        for name in ('404.html', 'robots.txt', 'sitemap.xml', '_headers', '.nojekyll',
                     'assets/site.css', 'assets/site.js', 'assets/favicon.svg',
                     'assets/favicon.ico', 'assets/social-card.png'):
            with self.subTest(name=name):
                self.assertTrue((SITE / name).is_file(), f'Missing publication asset: {name}')

    def test_social_metadata(self):
        meta = {attrs.get('property', attrs.get('name')): attrs.get('content')
                for tag, attrs in self.doc.tags if tag == 'meta'}
        self.assertTrue(meta.get('og:image'))
        self.assertEqual(meta.get('og:type'), 'website')
        self.assertEqual(meta.get('twitter:card'), 'summary_large_image')
        self.assertTrue(meta.get('description'))

    def test_editorial_cleanup(self):
        self.assertNotIn('discussed projects', self.source)
        self.assertNotIn('Logic is correct for the inputs', self.source)

    def test_local_links_and_ids(self):
        paths = [SITE / ENTRY] + [SITE / 'work' / s / 'index.html' for s in SLUGS]
        for path in paths:
            if not path.is_file():
                continue
            doc = Document(path.read_text())
            self.assertEqual(len(doc.ids), len(set(doc.ids)), f'Duplicate IDs: {path}')
            for tag, attrs in doc.tags:
                for key in ('href', 'src'):
                    raw = attrs.get(key, '')
                    url = urlsplit(raw)
                    if not raw or url.scheme or url.netloc:
                        continue
                    local_path = unquote(url.path)
                    if BASE and local_path:
                        self.assertTrue(local_path.startswith(BASE + '/'), f'Link escapes base path: {raw}')
                        local_path = local_path[len(BASE):]
                    target = SITE / local_path.lstrip('/') if local_path else path
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'Broken local link {raw} in {path}')
                    if url.fragment and target.is_file() and target.suffix == '.html':
                        self.assertIn(url.fragment, Document(target.read_text()).ids,
                                      f'Broken anchor {raw} in {path}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
