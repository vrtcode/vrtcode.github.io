import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuildModeTests(unittest.TestCase):
    def run_build(self, *args):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / 'site'
        result = subprocess.run([sys.executable, str(ROOT / 'build.py'), '--output', str(target), *args],
                                text=True, capture_output=True)
        return result, target

    def test_preview_does_not_claim_an_origin(self):
        result, target = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        source = (target / 'index.html').read_text()
        self.assertIn('noindex, nofollow', source)
        self.assertNotIn('rel="canonical"', source)
        self.assertNotIn('vrt.is-a.dev', source)
        self.assertIn('Disallow: /', (target / 'robots.txt').read_text())

    def test_project_pages_base_path(self):
        result, target = self.run_build('--production', '--site-url', 'https://example.github.io/portfolio')
        self.assertEqual(result.returncode, 0, result.stderr)
        source = (target / 'work/android-integrity/index.html').read_text()
        self.assertIn('href="/portfolio/assets/site.css"', source)
        self.assertIn('href="https://example.github.io/portfolio/work/android-integrity/"', source)
        self.assertIn('href="/portfolio/#work"', source)
        self.assertIn('src="/portfolio/assets/site.js"', source)
        self.assertIn('https://example.github.io/portfolio/work/android-integrity/', (target / 'sitemap.xml').read_text())

    def test_user_pages_and_custom_origin(self):
        for url in ('https://vrtcode.github.io', 'https://portfolio.example'):
            with self.subTest(url=url):
                result, target = self.run_build('--production', '--site-url', url)
                self.assertEqual(result.returncode, 0, result.stderr)
                source = (target / 'index.html').read_text()
                self.assertIn(f'href="{url}/"', source)
                self.assertIn('index, follow', source)
                self.assertIn('href="/assets/site.css"', source)
                self.assertNotIn('noindex', source)

    def test_missing_or_unsafe_origin_fails_closed(self):
        for args in (['--production'], ['--production','--site-url','http://example.com'],
                     ['--production','--site-url','https://user:password@example.com'],
                     ['--production','--site-url','https://example.com/?q=1'],
                     ['--production','--site-url','https://example.com/../escape']):
            with self.subTest(args=args):
                result, target = self.run_build(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((target / 'index.html').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
