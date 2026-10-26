"""Regression checks for the owner's biography and public Fenrir contribution."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class ProfileTests(unittest.TestCase):
    def test_experience_and_ethical_hacker_wording(self):
        home = (ROOT / 'dist/index.html').read_text()
        self.assertIn('18+ years', home)
        self.assertIn('ethical hacker', home)
        self.assertIn('websites, web services, mobile apps', home)
        self.assertNotIn('white-hat', home.lower())
        self.assertNotIn('white hat', home.lower())

    def test_fenrir_is_eighth_and_links_to_the_actual_contribution(self):
        cases = json.loads((ROOT / 'src/content.json').read_text())['cases']
        self.assertEqual(len(cases), 8)
        case = cases[-1]
        self.assertEqual(case['slug'], 'fenrir-tetris')
        self.assertEqual(case['num'], '08')
        self.assertIn('https://github.com/R0rt1z2/fenrir/pull/29', [a['href'] for a in case['publicLinks']])
        self.assertIn('https://github.com/vrtcode/fenrir/tree/codex/tetris-safe-profiles', [a['href'] for a in case['publicLinks']])
        self.assertIn('Tetris240910', case['approach'])
        self.assertIn('SHA-256', case['approach'])
        self.assertIn('closed without merge', case['disclosureNote'])
        self.assertIn('R0rt1z2', case['disclosureNote'])

    def test_eighth_route_and_cyclic_navigation(self):
        page = ROOT / 'dist/work/fenrir-tetris/index.html'
        self.assertTrue(page.is_file())
        source = page.read_text()
        self.assertIn('case 08 of 08', source)
        self.assertIn('href="/work/ios-attestation/"', source)
        self.assertIn('href="/work/android-integrity/"', source)
        self.assertNotIn('code and raw reports stay private', source)
        ios = (ROOT / 'dist/work/ios-attestation/index.html').read_text()
        self.assertIn('href="/work/fenrir-tetris/"', ios)
        self.assertIn('case 07 of 08', ios)


if __name__ == '__main__':
    unittest.main(verbosity=2)
