# zkfmi.com

Static site and technical documentation for the zkFMI stack
(zkPI, DeFMI, QOMM, OCLOB, DeKYX, DeCCP, Aethel).

## Layout

```
pages/       one HTML fragment per page (English), with a small header block
pages/ja/    the Japanese version of each page, same file name, same `path:`
static/      style.css, site.js, favicon.svg, robots.txt
charts.py    inline SVG charts, labels in both languages
build.py     wraps fragments in the shared template -> public/ (en at /, ja at /ja/)
tools/       check_ja.py: structural check of a Japanese page against its original
public/      the deployable site (generated; built in CI)
```

## Languages

Every English page has a Japanese counterpart under `pages/ja/` with the same
file name and header `path:`; the build writes it to `ja/<path>`, adds
`hreflang` alternates, a language switch in the header, and a separate
`ja/search.json`. Nav labels and UI strings live in `build.py` (`NAV_*`, `UI`),
chart labels in `charts.py` (`JA`). Writing rules and the glossary are in
`TRANSLATION_JA.md`; `python3 tools/check_ja.py` verifies that a translation
keeps the structure, code, numbers and links of the original and contains no
banned terms. A page without a translation still builds; its switch points at
the other language's index.

## Build

```sh
python3 build.py
```

No dependencies beyond the Python standard library. Mermaid diagrams render
client-side from cdnjs (pinned 11.15.0); everything else is inline.

## Preview

```sh
python3 -m http.server 8080 --directory public
```

## Deploy

`.github/workflows/pages.yml` builds `public/` and publishes it to GitHub
Pages on every push to `main` (Settings → Pages → Source: GitHub Actions).
The site is served at `https://zkfmi.com/ (the org project URL is https://zkfmi.github.io/zkfmi/ until the domain is bound)` until a custom domain
is configured.

The custom domain is a repository setting, not a file: Pages sites published
from Actions ignore `CNAME`. It was bound with

    gh api -X PUT repos/zkFMI/zkfmi/pages -f cname=zkfmi.com

DNS: A records 185.199.108.153 / .109.153 / .110.153 / .111.153 for the apex,
and a CNAME `www -> zkfmi.github.io`. The `ZKFMI_CNAME` variable only makes the
workflow write `public/CNAME` for other static hosts; GitHub does not read it.

## Analytics (Plausible)

Off by default. To enable, create the site `zkfmi.com` in Plausible, then set the
repository variable `ZKFMI_PLAUSIBLE_DOMAIN` to `zkfmi.com` (Settings → Secrets
and variables → Actions → Variables) and re-run the workflow. The build then
emits

    <script defer data-domain="zkfmi.com" src="https://plausible.io/js/script.outbound-links.js"></script>

in every page's `<head>` and a "no cookies" note in the footer. For a
self-hosted Plausible set `ZKFMI_PLAUSIBLE_SRC` to your instance's script URL.
If Plausible gives you a different snippet (per-site `pa-…js` scripts), paste it
verbatim into `ZKFMI_ANALYTICS_HTML` instead; that variable wins when set.

Locally: `ZKFMI_PLAUSIBLE_DOMAIN=zkfmi.com python3 build.py`.

