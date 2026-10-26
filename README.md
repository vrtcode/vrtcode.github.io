# vrt — Security Research & Engineering

An English-only personal portfolio with conversational technical copy, prepared for **GitHub Pages**.

Repository: [vrtcode/vrtcode.github.io](https://github.com/vrtcode/vrtcode.github.io).
The intended initial Pages address is `https://vrtcode.github.io/`; repository creation does not mean that Pages has been enabled or the website deployed.

## What is included

- The supplied graphite/cyan/lime design, original layout, case-study diagrams, and optional network background.
- Ten real HTML pages: home, eight case studies, and a not-found page.
- Local IBM Plex fonts, favicon, 1200 × 630 social preview, per-page metadata, and an origin-aware sitemap.
- A Python standard-library build. No Node, npm, React, API keys, package installation, or network access is needed to build or serve the website.
- Optional progressive enhancement for the mobile menu and background. Content and navigation work without JavaScript.
- Read-only CI on pushes and pull requests, plus a **manual** GitHub Pages publication workflow.

## Local preview

Requirements: Python **3.10 or later**. CI uses Python 3.13.

```sh
python3 build.py
python3 serve.py
```

Open `http://127.0.0.1:8768/`. Stop the server with Ctrl+C. The server binds to loopback only and serves the generated `dist/` directory, not source files.

Do not open the HTML directly as `file://`: it uses origin-relative links, as expected for a hosted website. `serve.py` supplies the appropriate base path and a real local HTTP 404 response.

The default build is an intentionally **non-indexable preview**: no invented canonical origin, `noindex, nofollow`, and `Disallow: /`. It must be rebuilt in production mode before public release.

## GitHub Pages publication

The repository name `vrtcode.github.io` is the user-site convention. A different repository name also works: the build supports a project-site subpath automatically.

1. In this repository, open **Settings → Pages**.
2. Set the build and deployment source to **GitHub Actions**.
3. Open **Actions → Publish GitHub Pages → Run workflow** on the default branch.
4. Wait for both the `build` and `deploy` jobs to finish. Inspect the deployment URL shown by the workflow.
5. Verify the public home page, a direct case-study URL, a missing URL, fonts, and social metadata.

The publication workflow obtains the actual URL from the official `actions/configure-pages` action. It passes `base_url` to the production build; that value includes a project subpath or configured custom domain when applicable. It uploads **only `dist/`**, never the source directory.

Publication through the supplied workflow is manual on purpose. A normal push runs tests, not that deployment. The hosting setting must also be **GitHub Actions**: a user-site repository configured for legacy branch publishing can separately auto-publish its README/source. That legacy behavior was observed after the first push and the source setting was corrected; see `VERIFICATION.md` for the remaining old-deployment cleanup. No personal access token, repository secret, or third-party deployment account is required: the official deployment action uses the workflow's narrowly scoped GitHub permissions and OIDC.

After the first approved deployment, automatic updates can be enabled by adding a `push` trigger restricted to the default branch in `.github/workflows/pages.yml`. Keep the tests and deploy job dependency intact.

## Production build without GitHub Actions

Supply the **actual** public HTTPS address:

```sh
python3 build.py --production --site-url https://vrtcode.github.io
python3 -m unittest discover -s tests -v
```

For a project repository:

```sh
python3 build.py --production --site-url https://YOUR-ACCOUNT.github.io/YOUR-REPOSITORY
python3 serve.py
```

That example generates prefixed asset/navigation URLs and matching canonical and sitemap URLs. Replace the example account and repository; it is not a claim that such a deployment exists.

To test a local subpath without claiming a public origin:

```sh
python3 build.py --base-path /portfolio
python3 serve.py
```

Open `http://127.0.0.1:8768/portfolio/`.

`--output` accepts a separate destination. Rebuilding replaces generated files at that destination; use a dedicated build directory, not a folder containing unrelated documents. The builder performs no deployment and does not initialize or change Git state.

## Connecting vrt.is-a.dev later

The subdomain is a target, **not a registered or verified domain**. There is intentionally no `CNAME` file in this project and no claim of ownership in preview metadata.

First publish the completed portfolio at its working GitHub Pages address. Then follow the current is-a.dev documentation and manually submit the domain application, using `vrtcode` as the GitHub owner and the real preview URL. Do not submit placeholder website links or claim requirements that are not met.

The documented GitHub Pages DNS target is `vrtcode.github.io`, without a protocol or path. After registration is approved, configure the custom domain in GitHub Pages settings and enable HTTPS when available. Re-run the publication workflow so canonical, social-image, and sitemap URLs use the configured domain. Follow any required verification and DNS propagation steps before calling the domain operational.

The is-a.dev terms allow AI-assisted website development but warn against AI-created registration pull requests. This project does not submit or generate that application on the owner's behalf.

## Editing the website

| File | Responsibility |
|---|---|
| `src/content.json` | Case studies, diagrams, focus areas, approach, and tool groups |
| `src/body.html` | Hero, About, section structure, case-page structure, contact, and footer |
| `src/header.html` | Brand and accessible primary navigation |
| `src/social-card.html` | Editable source for the checked-in social-preview image; not a runtime page |
| `src/base.css` | Original global visual rules |
| `src/enhancements.css` | Local font declarations, header/menu layout, and responsive refinements |
| `assets/site.js` | Optional menu and background behavior |
| `assets/` | Fonts, licenses, icons, and social image |
| `build.py` | Static rendering, metadata, sitemap, robots, and build hashes |
| `serve.py` | Local-only preview with real 404 behavior |
| `.github/workflows/check.yml` | Read-only build and validation |
| `.github/workflows/pages.yml` | Explicitly initiated Pages publication |

The small template syntax in `src/body.html` is resolved **during the Python build**, never in the browser. Generated pages contain no template bindings, editor bridge, runtime compiler, or CDN imports. Trusted SVG fragments in `src/content.json` are maintained as project source, not accepted from remote or user-generated input.

Update existing data rather than editing files in `dist/`; rebuilding rewrites those outputs; removed source assets may leave stale files in an existing output directory, so use a fresh dedicated directory for release artifacts. Keep public claims bounded by evidence. The private project notes and original design-support runtime are not included in the repository.

## Validation

```sh
python3 build.py
python3 -m unittest discover -s tests -v
```

The suite checks static content, English document language, eight real case pages, local links/anchors, unique IDs, absence of browser templates/CDN dependencies, assets, editorial corrections, preview safety, valid production URLs, and GitHub project subpaths.

An optional browser suite is provided in `tests/browser.cjs`. It requires a separately available Playwright package and Chromium; these are **QA-only**, not build or website dependencies. Run it in an environment where `require('playwright')` resolves:

```sh
node tests/browser.cjs
```

If using an existing Chrome installation, set `BROWSER_EXECUTABLE` to its executable path. The test starts and stops its own loopback preview server. It checks all pages at four viewport widths with JavaScript enabled and disabled, SVGs, fonts, menus, reduced motion, HTTP 404, and external resource requests. Results go to ignored `test-results/` by default.

Useful optional environment variables: `VRT_TEST_SITE` for another built directory, `VRT_TEST_PORT` for another local port, and `VRT_REPORT_DIR` for an alternate report destination. Additional QA software or browser installation is an explicit local action, not something the build performs.

For code-level comparison with the **reviewed owner-supplied original design** (not included in this repository):

```sh
python3 tests/compare_design.py /path/to/reviewed-design.html
node tests/compare_background.cjs /path/to/reviewed-design.html
```

The Python check compares the original global CSS, body template, and header declarations against an explicit migration-change list. The Node check runs only the extracted, reviewed background method in a mocked Canvas environment and compares every drawing command with the static implementation. Do not pass an unreviewed or remotely fetched template: Node's VM is a test harness, not a security boundary. These checks need no npm packages and make no network requests.

See `DESIGN_PARITY.md` for the source-code mapping and every intentional difference. See `VERIFICATION.md` for the checks actually performed and the remaining public-deployment gates. Passing local tests is not proof of a live Pages deployment or a complete accessibility certification.

## Security and privacy

No analytics, forms, cookies, API calls, or third-party rendering resources are included. Hosting providers may retain access logs; do not claim that no data is collected anywhere.

HTML carries a restrictive Content Security Policy and referrer policy. Scripts are local and do not need `unsafe-eval`. Inline SVG style attributes require the documented style policy; there are no inline event handlers.

`dist/_headers` is a portability aid for hosts that support it. **GitHub Pages does not apply `_headers` files or provide arbitrary custom response headers.** Do not claim that X-Frame-Options, frame-ancestors, or MIME-sniffing protection from that file are enforced on Pages. The HTML CSP deliberately omits header-only `frame-ancestors` to avoid a false claim.

Never add secrets, original traces, device identifiers, private reports, or unapproved vulnerability disclosures. GitHub Actions dependencies are pinned to the official action commit SHAs verified during preparation; review updates before changing pins.

## Profile and public contribution

The owner describes 18+ years of cybersecurity and vulnerability research across websites, web services, mobile apps, APIs and related systems. The public role wording is **ethical hacker**, not “white-hat.” This biography is owner-supplied, not a separate employment-history verification.

Case 08 describes the owner's [Fenrir PR #29](https://github.com/R0rt1z2/fenrir/pull/29), not authorship of the whole upstream project. The PR head was inspected at `9f7f9c9257a4d05f38c698e7c838d515de170f82`; it was closed without merge at review time. Links target the actual PR and contribution branch, not only the fork's unrelated default branch. See `verification/profile-update.json` for source provenance.

Cases can provide `sourceNote` and a `publicLinks` array. Private cases keep an empty link array; a public case must not inherit an “all code is private” statement. Both cards and previous/next navigation include the eighth case, and the displayed total is generated from the data.

## Fonts and design provenance

IBM Plex Sans and IBM Plex Mono are distributed under the SIL Open Font License, included at `assets/fonts/OFL.txt`. The runtime WOFF2 files match the Latin font resources requested by the supplied design from Google Fonts. Their original Unicode ranges are retained so symbols outside those ranges use the same system fallback as the design. See `assets/fonts/SOURCES.md` for provenance.

The visual design was supplied by the owner and retained during migration. No general license grant for the portfolio's code, copy, or supplied design is implied by the fonts' license.

## Reference documentation

- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Official configure-pages action and outputs](https://github.com/actions/configure-pages)
- [is-a.dev registration guide](https://docs.is-a.dev/quickstart/)
- [is-a.dev GitHub Pages guide](https://docs.is-a.dev/guides/github-pages/)
- [is-a.dev terms](https://github.com/is-a-dev/register/blob/main/TERMS_OF_SERVICE.md)
