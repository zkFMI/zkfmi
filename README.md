# zkfmi.com

Static site and technical documentation for the zkFMI stack
(zkPI, DeFMI, QOMM, OCLOB, DeKYX, DeCCP, Aethel).

## Layout

```
pages/     one HTML fragment per page, with a small header block
static/    style.css, site.js, favicon.svg, CNAME, robots.txt
build.py   wraps fragments in the shared template -> public/
public/    the deployable site (generated; commit it or build in CI)
```

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
The site is served at `https://shukob.github.io/zkfmi/` until a custom domain
is configured.

To switch to zkfmi.com: point DNS at GitHub Pages (A records
185.199.108.153 / .109.153 / .110.153 / .111.153 for the apex, and a CNAME
`www → shukob.github.io`), then set the repository variable `ZKFMI_CNAME` to
`zkfmi.com` (Settings → Secrets and variables → Actions → Variables) and
re-run the workflow. The workflow writes `public/CNAME` from that variable;
`CNAME.example` is the reference value. Any other static host serves
`public/` unchanged.

## Editing

- Page order in the sidebar is in `build.py` (`NAV_DOCS`); file names in
  `pages/` only order the build.
- Headings `<h2 id="...">` in docs pages feed the on-page table of contents.
- Numbers on the site come from the repositories' `artifacts/*.json` and the
  generated `DEFMI.md` / `AUDIT.md`. When those regenerate, update
  `docs/measurements.html` and the figures quoted on the landing page.
- The "not claimed" lists are copied from `REVIEW.md`, `REGULATION.md` §9,
  `STATUS.md` and `THREAT_MODEL.md`. Keep them in step with the code.
