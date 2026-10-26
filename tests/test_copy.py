"""Checks for the approved conversational-English copy revision."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class CopyTests(unittest.TestCase):
    def test_home_voice_and_metadata(self):
        home = (ROOT / 'dist/index.html').read_text()
        self.assertIn("Figure out what's", home)
        self.assertIn('really going on.', home)
        self.assertIn('No hype. Just receipts.', home)
        self.assertNotIn('The personal portfolio of vrt:', home)

    def test_case_copy_is_rewritten_without_changing_routes(self):
        content = json.loads((ROOT / 'src/content.json').read_text())
        expected = {
            'android-integrity': 'Android integrity: under the hood',
            'realtime-security': 'WebSockets: auth before anything else',
            'worker-lifecycle': 'Workers that know when to quit',
            'mobile-sdk-analysis': 'Mobile SDKs: same request, different story',
            'push-integration-security': "Push pipelines: queued isn't delivered",
            'network-observability': 'Network debugging: one layer at a time',
            'ios-attestation': 'iOS attestation: claims vs. receipts',
        }
        self.assertEqual({c['slug']: c['title'] for c in content['cases']}, expected)
        for case in content['cases']:
            self.assertEqual(case['href'], '/work/' + case['slug'] + '/')
            self.assertTrue(case['disclosureNote'])
            self.assertTrue(any(e['label'] == 'The catch' for e in case['evidenceList']))

    def test_case_link_names_include_visible_words(self):
        cases = json.loads((ROOT / 'src/content.json').read_text())['cases']
        for case in cases:
            self.assertIn('Dig into it', case['linkLabel'])

    def test_attestation_limits_remain_explicit(self):
        cases = json.loads((ROOT / 'src/content.json').read_text())['cases']
        android = next(c for c in cases if c['slug'] == 'android-integrity')
        ios = next(c for c in cases if c['slug'] == 'ios-attestation')
        self.assertIn('no accepted official verdict', android['disclosureNote'])
        self.assertIn('no attestation bypass', ios['disclosureNote'])
        self.assertIn('no accepted server-side result', ios['disclosureNote'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
