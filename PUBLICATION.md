# Verified GitHub Pages publication

Date: 2026-10-26. The owner explicitly approved publishing the correct build.

- Live portfolio: [vrtcode.github.io](https://vrtcode.github.io/).
- Eighth case: [Fenrir: a safer Tetris port](https://vrtcode.github.io/work/fenrir-tetris/).
- Successful manual workflow: [Publish GitHub Pages — 40250774256](https://github.com/vrtcode/vrtcode.github.io/actions/runs/40250774256).
- Immutable deployed source: `2a343a602ed84480ab99f92f5c92585a298030fa`.
- Both build and deploy jobs succeeded. The build ran the 20-test suite before uploading **only `dist/`**.

The hosting source is GitHub Actions. The earlier automatic legacy README deployment has been replaced by this approved artifact. Documentation receipts committed later do not change the deployed HTML/assets; the source revision above identifies the actual release.

## Independent public verification

HTTP checks used the public HTTPS address, not a local preview or the Actions result alone:

- Published production manifest exactly equals the independently built manifest for the deployed source.
- **22 public files** match their expected SHA-256 byte for byte: all ten HTML files, CSS/JavaScript, all three fonts, icons, social image, font provenance/license, robots and sitemap.
- GitHub-hosting control files `.nojekyll` and `_headers` are not counted as browser resources. GitHub Pages does not apply `_headers` as response-header configuration.
- Four missing paths return **HTTP 404** and our exact custom 404 body: a nonexistent route, `/src/content.json`, `/build.py`, and `/README.md`. The source repository is public, but its root is no longer served as the website artifact.

Fresh Chrome checks against the public site passed **20 page/viewport combinations**: home, eight cases and a missing route at 390 and 1440 px. Checks cover one H1, no overflow, loaded local fonts, eight cards, `ethical hacker` and `18+ years` copy, canonical/social metadata, production indexability, case 08 and its actual PR link, mobile menu/Escape/focus, zero page errors, and zero external rendering requests. Published mouse attraction passed a separate deterministic frame test.

Receipts: `verification/publication-http.json`, `verification/publication-browser.json`, and `verification/github-publication.json`.

## Reproduction and rollback boundary

To build the release format locally:

```sh
python3 build.py --production --site-url https://vrtcode.github.io
python3 -m unittest discover -s tests -v
```

Publication remains manual. A normal push does not redeploy the site. To reproduce the exact approved release, re-run the successful workflow run linked above; its original source SHA identifies the known-good revision. Any later functional change needs fresh checks and another approved deployment.

This release does not claim Safari/WebKit or real-phone testing, a complete screen-reader audit, a performance score, or registration of `vrt.is-a.dev`. The custom domain is a separate gate; no CNAME is configured.
