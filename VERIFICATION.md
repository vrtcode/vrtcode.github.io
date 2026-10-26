# Verification record

Date: 2026-10-26. Scope: source migration, project preparation, and the later explicitly approved GitHub Pages release. The pre-release checks below are supplemented by `PUBLICATION.md` and independent public receipts. No custom-domain registration is claimed.

## Source and visual fidelity

See `DESIGN_PARITY.md` for the code-to-code inventory, original-file hash, fixes, and every intentional difference.

- Original global CSS: exact match.
- Main body template: no unlisted differences after the explicit migration substitutions.
- Header: 17 styled definitions, 86 original declarations, both hover rules checked.
- Fourteen SVGs / 400 elements: original coordinates, attributes, styles, shapes and visible labels preserved; two iOS accessible descriptions reworded.
- Background: twelve configurations, 438 steps, **453,807 exactly equal Canvas commands** between the original method and migrated script.
- Browser supplement: 505 matched main-content elements × 57 computed properties at 390 and 1440 px; original and static canvas PNGs identical under seeded static conditions. Small interpolation-wrapper rounding and intentional copy-wrap differences are documented, not represented as exact whole-page pixel parity.
- Local fonts match the design's original Google Fonts Latin WOFF2 resources and Unicode ranges.

Reproducible source checks, both exit code 0:

```sh
python3 tests/compare_design.py /path/to/reviewed-design.html
node tests/compare_background.cjs /path/to/reviewed-design.html
```

The original template is not committed. The Node comparison requires the reviewed local template, not an untrusted fetched file.

## Build and static checks

```sh
python3 build.py
python3 -m unittest discover -s tests -v
```

Result: **20 tests passed**, exit code 0. Before implementation, the original export failed the static acceptance suite with 25 assertions across nine tests. Build-mode tests were introduced separately and first failed before their implementation.

The suite checks real case pages, resolved templates, local resources, English language, unique IDs, local links/anchors, publication assets, metadata, explicit copy corrections, safe preview behavior, production origins, and Pages subpaths. Invalid or missing production origins fail closed.

Additional commands, exit code 0:

```sh
python3 -m py_compile build.py serve.py tests/compare_design.py
node --check assets/site.js
node --check tests/compare_background.cjs
python3 build.py --output project-dist --production --site-url https://example.github.io/portfolio
VRT_SITE=project-dist python3 -m unittest discover -s tests -p test_static.py -v
```

Result: **nine project-subpath acceptance tests passed**. The example URL is a fixture, not a deployment.

## Browser checks

Engine: installed Google Chrome via Playwright. QA software is separate from the website/build dependencies.

```sh
BROWSER_EXECUTABLE=/path/to/chrome node tests/browser.cjs
```

Root-site result: **80 page/viewport/JavaScript combinations passed**, exit code 0. Matrix: home, eight case pages and a missing URL; viewport widths 360, 390, 768 and 1440; JavaScript on and off.

Observed:

- One H1, English document language, no horizontal overflow, loaded local fonts and usable SVGs.
- Direct page loads return HTTP 200; the missing route returns the custom page with real HTTP 404.
- Mobile navigation opens, closes, handles Escape, returns focus and focuses selected sections.
- Navigation/content remain available without JavaScript.
- Zero external rendering-resource requests and zero page errors in the tested matrix.
- Reduced-motion background remains static.
- Mouse-attraction regression test passes: pointer movement toward the cursor and return after mouse leave are measured in `verification/browser.json`. Inputs deliberately exercise attraction rather than merely checking cursor lines.

The attraction test was first observed red on the migrated code (1.123 px of incidental drift), then passed after restoring the original physics. The same regression assertions remain in `tests/browser.cjs`.

The same full browser suite also passed **80 combinations** against the production-mode `/portfolio` project-subpath build (160 route/viewport/JavaScript combinations across the two builds). This closes local browser coverage of prefixed assets, menu links and direct routes; it does not prove a public Pages deployment.

Receipts: `verification/browser.json`, `verification/browser-project-subpath.json` and `verification/background-code-parity.json`.

## Local Lighthouse checks

Mobile navigation audits on the final production-mode local build:

| Page | Accessibility | Best practices | SEO |
|---|---:|---:|---:|
| Home | 100 | 100 | 92 |
| Fenrir contribution case | 100 | 100 | 92 |

The only failed audit is Lighthouse's robots.txt download. The page-context download is blocked by the deliberate `connect-src 'none'` policy. Independent HTTP retrieval returned 200, `text/plain`, and the expected production robots/sitemap content. The policy was not weakened to improve a score. This local audit does not establish public crawler behavior.

This Lighthouse tool excludes performance. No performance score, real-device audit, full screen-reader test, Firefox or Safari/WebKit result is claimed. Automated accessibility 100 is not a complete accessibility certification.

## Conversational copy regression checks

The copy rewrite began with three red copy tests, then passed after implementation. A follow-up Lighthouse run found that “Dig into it” was missing from the expanded accessible case-link names. A specific regression test was added red, the names were corrected, and the same test passed. The final Lighthouse runs show no label/name mismatch; the only remaining failed audit is the documented robots.txt gathering issue.

Current checks after the eighth-case extension: 20 unit/static tests; 80 root-site and 80 project-subpath browser combinations; 54 additional page/viewport checks across 360, 390, 768, 860, 1024 and 1440 px, with no page overflow or SVG text outside its viewBox. CSS, fonts, header styles and background drawing behavior were not changed by the copy rewrite.

## Eighth-case and biography checks

Three new regression tests were first red and then passed: 18+ years plus ethical-hacker wording; case 08 linked to the actual Fenrir PR and branch with accurate credit/status; and the eighth route, displayed `08 of 08` count, private/public source text, and cyclic navigation.

Fenrir source review was read-only. The actual PR diff, not only the default branch or README, supports the descriptions of the image-hash gate, firmware-specific profile and patch guards. No Fenrir build, flash script, device mutation, firmware rollout, or new attestation test was performed for the portfolio. The saved 24-build firmware-analysis report was re-read; it is not a fresh device or server measurement.

## GitHub and publication boundary

- Target repository: [vrtcode/vrtcode.github.io](https://github.com/vrtcode/vrtcode.github.io).
- Push/PR CI is read-only. The Pages publication workflow requires explicit manual dispatch.
- The manual `Publish GitHub Pages` workflow was **not** dispatched. After the first source push, GitHub nevertheless ran its built-in **legacy Jekyll Pages deployment** from `main:/`, rendering the repository README instead of the portfolio build.
- Independent Pages API and public HTTP checks confirmed that legacy deployment. The source was then changed to **GitHub Actions** (`build_type=workflow`) to stop branch-based auto-publication. Two attempts to deactivate the site through the Pages REST API returned HTTP 422 (“Deactivating GitHub pages for this repository is not allowed”).
- This was resolved after explicit owner approval to publish: manual workflow run **40250774256** deployed the intended production artifact from `2a343a602ed84480ab99f92f5c92585a298030fa`. Independent HTTP and browser checks confirmed the actual portfolio replaced the README. No separate unpublish step remains. See `PUBLICATION.md`.
- Read-only CI passed for source revision `af8c751e54519dac925bc35689cf857f989b8926`: [Check static site](https://github.com/vrtcode/vrtcode.github.io/actions/runs/40250314527). The built-in legacy run is [40250311631](https://github.com/vrtcode/vrtcode.github.io/actions/runs/40250311631), not the manual publication workflow.
- `vrt.is-a.dev` is an intended future domain, not registered/verified by this project. There is no CNAME file.
- `_headers` is supplied only for compatible hosts. GitHub Pages does not apply it; HTML CSP remains the applicable local policy mechanism.

## Remaining release gates

1. **Closed:** source CI and the deployment workflow passed for the published revision; subsequent documentation edits run separate read-only CI.
2. **Closed:** GitHub Actions is the Pages source and the owner-approved production workflow deployed successfully, replacing the unintended README site.
3. **Closed:** public checks cover all ten pages, direct routes, real custom HTTP 404, fonts, canonical/social metadata, sitemap, robots, menu, and pointer attraction. The published manifest and 22 public-file hashes match the intended build.
4. Check Safari/WebKit, a real mobile device and keyboard/screen-reader behavior before claiming broad browser/accessibility coverage. Measure performance separately.
5. Apply for the domain manually under the current is-a.dev rules, then verify ownership/DNS/HTTPS and rebuild metadata against the actual public domain.

The independent public checks close the requested GitHub Pages publication gate. Broader browser/accessibility/performance coverage and custom-domain registration remain separate work.
