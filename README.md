# frontend/ — the SkillXray website

The public face of the project: landing page + scanner, in one self-contained
`index.html` (no framework, no build step, no external assets; light & dark themes).

## How it finds the backend

The page picks its API base automatically (see `var API` in `index.html`):

- served **by the backend** (port 8080, locally or on a server) → same origin;
- served anywhere else (GitHub Pages, `file://`, a static dev server) → the
  visitor's own local backend at `http://localhost:8080`.

So the deployed site does live scans for anyone running the backend locally,
and shows the landing page + recorded demo to everyone else. The backend lives
in the private `SkillAppropriateness` repo (it wraps unpublished pipeline code
and needs VPN-only model access, so it is not part of this repo).

## Run locally

```bash
open frontend/index.html                  # page only, or:
python3 -m http.server 8000 -d frontend   # -> http://localhost:8000
```

For live scans, also start the backend (see `DEPLOY.md` in the backend repo) —
or just open http://localhost:8080, where the backend serves this page itself.

## Deploy (GitHub Pages)

Pushing to `main` publishes `frontend/` via `.github/workflows/pages.yml`.
The workflow tries to enable Pages on its own; if its configure step fails
with a permissions error, the repo owner does the one-time setup instead:
Settings → Pages → Source: **GitHub Actions**. Site:
https://keerthi166.github.io/SkillXRay/
