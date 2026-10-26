# Source-code and design migration audit

Date: 2026-10-26. The original design was compared as source code first; rendered-browser checks supplement that comparison.

Original file: `vrt Portfolio v2.dc.html`.

Original SHA-256: `9b5b4f8965c9679e847055880e2c83992297f2220bd2041ccbe7e9d43292a5cd`.

The original file was not modified. The private design-support runtime is not included in this repository.

## Later copy revision

After the migration baseline, the owner requested conversational technical English across the public site. This revision changes text, not the visual/behavioral code: `src/base.css`, `src/enhancements.css`, and `assets/site.js` remain byte-identical to the baseline. The 14 SVG trees retain all 400 elements and their geometry, attributes and styles; 90 text nodes were intentionally rewritten. The journal `verification/copy-rewrite.json` records 64 template-text replacements and 173 data-string changes. Metadata and the social-preview copy were updated too.

The exact-text and computed-style receipts below describe the original migration baseline, not a promise that rewritten text has identical line wraps. The source comparison now applies the explicit copy journal before checking the body; it still rejects unlisted markup/style changes. Current browser receipts cover the rewritten copy.

## Eighth case and owner biography

A later owner request adds 18+ years of experience, the role “ethical hacker,” and case 08 about the owner's actual Fenrir contribution. This is an intentional extension to the seven-case supplied design, not a missing original block. The existing seven cases keep their SVG geometry and visual code. Two new diagrams use the same palette, typography, line/box style and card/page sizes.

The code comparison applies the explicit body changes recorded in `verification/profile-update.json`: biography text, public/private work wording, and an optional public-source link loop. Global CSS, header declarations, local font resources and background behavior remain unchanged. The original migration and pre-extension visual receipts below are historical baselines; current browser receipts cover all eight cases.

## Code conservation

| Original source | Static implementation | Result |
|---|---|---|
| Global `<style>` | `src/base.css` | Exact byte-for-byte match after trimming the export boundary |
| Body template outside the site header | `src/body.html` | Exact match after the explicit substitutions below; no style declarations changed |
| Header's 17 styled element definitions | `src/header.html`, `src/enhancements.css` | All 86 original declarations and both hover rules match; equivalent `clip:rect(...)` syntax normalized |
| `style`, `style-hover`, `style-focus` attributes | `build.py:Renderer` | Converted into local CSS classes, `:hover`, and `:focus`; not dropped |
| `sc-if`, `sc-for`, and text bindings | Python build + `src/content.json` | Resolved at build time, absent from generated browser HTML |
| `diagram()` / `DIAGRAMS` | Fourteen embedded SVG trees in `src/content.json` | All 400 elements, coordinates, attributes, styles and visible text match; two iOS accessible descriptions intentionally reworded |
| `CASES`, flow, focus, steps, layers, tools | `src/content.json` | All collections retained; 24 changed leaf paths explicitly inventoried, none unexplained |
| Previous/next case selection | `build.py:build` | Same cyclic indexing, `(i-1) % count` and `(i+1) % count` |
| `wide` / `narrow` (`w < 860`) | CSS media query / `matchMedia` | Same 860 px breakpoint |
| Menu toggle, Close/Menu label, Escape | `assets/site.js` | Retained; keyboard-focus recovery and no-JavaScript navigation added |
| `startNet()` / animation frame | `assets/site.js` | Exact Canvas-command parity under the tested inputs below |
| Grid backdrop | `src/body.html` | Original 56 px grid, 1100 px height, gradient opacity, masks, and stacking preserved |

### Explicit body substitutions

1. Site header replaced by the static header partial, with its styles audited separately.
2. The React canvas ref replaced by the `network-bg` DOM ID.
3. The Tools introduction no longer refers to a private conversation: “Tools used across research and engineering projects.”
4. The hard-coded case total `07` replaced by a build-time total, still rendered as `07` with the present seven cases.
5. The Evidence introduction now distinguishes implementation notes, principles, and open questions rather than implying fresh verification.

Outside the header/ref substitutions, the body diff consists of exactly the three text/count changes in items 3–5. All inline visual declarations, hover attributes, and focus attributes remain in the source template.

### Content changes, not lost features

The 24 changed data paths comprise seven case URLs, nine evidence labels, four verification-layer statements, iOS context and disclosure text, and two iOS SVG accessible descriptions. Full paths are recorded in `verification/content-change-paths.json`.

Evidence labels now say “Implementation” or “Principle” instead of calling every statement “Established.” iOS text no longer equates application-level observations with a hardware or accepted-attestation guarantee. Case titles, summaries, topics, focus areas, approach steps, tool lists, diagram shapes, and visible diagram text are retained.

## Background: code-level equivalence

The original `startNet()` method and the new script ran with identical seeded randomness and mocked Canvas contexts. Every drawing operation and style assignment was compared, not only the final image.

- Viewports: 390 × 1000 and 1440 × 1000.
- Device pixel ratios: 1, 2, and 3; original DPR cap of 2 retained.
- Reduced motion: on and off.
- Twelve configurations, 438 comparison steps, **453,807 exactly matching Canvas commands**.
- Tested initial render, drift, mouse attraction, mouse leave/return, and reduced-motion resize.

| Parameter / mechanism | Retained original value |
|---|---|
| Node count | `min(120, round(width * height / 13000))` |
| Drift velocity | `(random - 0.5) * 0.12` |
| Node radius | `2.2` with probability `0.12`, otherwise `1.3` |
| Lime probability | `0.08` |
| Cyan node fill | `rgba(102,217,239,.45)` |
| Lime node fill | `rgba(181,224,122,.55)` |
| Attraction radius / strength | `210` / `(1 - distance / 210) * 0.45` |
| Position easing | `0.08` |
| Node-link radius / alpha | `135` / `0.16 * (1 - distance / 135)` |
| Cursor-link radius / alpha | `147` / `0.22 * (1 - distance / 147)` |
| Line width / alpha precision | `1` / three decimal places |
| Node arc | `0` to `6.283` |
| Draw order | Update positions → node links → cursor links → node circles |

Lifecycle changes are intentional: mouse `pointermove` replaces `mousemove`; hidden documents pause drawing; reduced-motion changes are observed live; page hide/show handles browser restoration. Touch input does not enable mouse attraction. Editor-only visual preview controls are replaced by the shipped defaults and source configuration, not exposed as public UI.

## Fonts, shadows and visual states

Runtime fonts now use the exact three Latin WOFF2 resources fetched by the supplied design, with the original Unicode range. This restores the original system fallback and width of arrow symbols. Fonts are served locally; see `assets/fonts/SOURCES.md` for URLs and hashes.

The original source has **zero `box-shadow` and zero `text-shadow` declarations**. None were invented. The translucent surfaces, 10 px header backdrop blur, borders, corner decorations, focus outline, card backgrounds, and hover transitions are retained.

Unintended migration differences found and corrected:

- Missing node attraction, altered node drift/density and drawing appearance.
- Reduced background opacity and an artificial frame-rate cap.
- Header background alpha changed from `0.86`, and its GitHub hover transition omitted.
- Mobile navigation labels, separators, background, padding and 52 px link height altered.
- Anchor offset changed from 64 px; extra SVG overflow override added.
- Full-font fallback behavior changed the width of arrow symbols; original local WOFF2 subsets/ranges now restored.

## Supplemental browser comparison

At 390 and 1440 px, 505 main-content elements per page were matched after ignoring the export runtime's interpolation-only wrappers. Fifty-seven computed properties per element cover fonts, colors, opacity, shadows, borders, spacing, dimensions, transitions, transforms and SVG presentation. All compared font/color/shadow/border declarations match. Six desktop hover targets match across the compared properties; mobile menu labels and styling match.

The canvas PNGs are byte-identical between original and static pages for both widths under identical seeded positions and reduced-motion settings. This proves the tested initial appearance, not universal cross-browser pixel equivalence.

Remaining computed differences are explained, not hidden:

- Seven “case 01” labels differ by **0.0156 CSS px** in computed width because the editor's separate interpolation spans were removed. Their CSS and font resources match; no compensating spacing hack was introduced.
- On 390 px, ten ancestor/paragraph height differences arise from the intentional Tools and verification-layer copy edits and their line wraps. At 1440 px these height differences disappear.

## Intentional static-site architecture changes

- React/editor lifecycle, `support.js`, runtime compilation, refs and hash-based case routing are not public dependencies. Real `/work/<slug>/` pages replace editor hash routes; legacy `#/work/...` URLs are not a compatibility promise.
- Normal links and real browser navigation replace `sync()` / `goTop()` state updates. Section scrolling retains the original 64 px offset.
- `initialView` is an editor preview control; separate real pages and the HTTP 404 page replace it.
- `showGrid` and `cardDiagrams` are source configuration, enabled as in the supplied default. Removing the optional script disables the animated background and menu enhancement without hiding content.
- No-JavaScript mobile navigation remains visible. With JavaScript it collapses behind Menu, closes on Escape and section selection, and restores keyboard focus.
- A static build, metadata, local assets, real 404 behavior and manual GitHub Pages workflow are publication additions, not claims of a deployed website.

## Reproduce the source checks

Review the original local template before running the optional Node comparison. The VM is not a security boundary and this test must not consume an unreviewed remote template.

```sh
python3 tests/compare_design.py /path/to/reviewed-design.html
node tests/compare_background.cjs /path/to/reviewed-design.html
```

Both commands completed with exit code 0 during this audit. The original design is intentionally not committed. Numeric receipts are stored in `verification/`; see `VERIFICATION.md` for functional checks and remaining gates.
