# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

SkillXRay is a research prototype (IBM Research) that generates "Privacy Facts" labels for AI-agent skills by statically analyzing their code. It reveals what a skill's code *actually does* with user data versus what its description claims.

The pipeline: fetch skill → parse SKILL.md + code → find data moves (read/save/send/infer/delete) → identify violations via Contextual Integrity → name harms via Solove's taxonomy → render a Privacy Facts card.

## Repository structure

This repo contains only the public frontend. The backend (scan pipeline, API server) lives in the private `SkillAppropriateness` repo (`code/SkillAppropriateness` relative to the parent monorepo), which requires VPN access.

- `frontend/index.html` — entire frontend: landing page + scanner UI, no framework, no build step
- `frontend/analyzer.js` — **auto-generated**; the client-side analysis engine (see below)
- `frontend/config.js` — set `window.SKILLXRAY_API_BASE` for deployed environments
- `frontend/findings-data.json` — snapshot of the August 13, 2026 corpus run (54 skills)
- `frontend/scripts/build_analyzer.py` — regenerates `analyzer.js` from backend prompt sources
- `frontend/scripts/build_findings.py` — rebuilds `findings-data.json` from a results folder
- `.github/workflows/pages.yml` — publishes `frontend/` to GitHub Pages on push to `main`

## Frontend

**No build step.** Edit `frontend/index.html` directly.

Run locally:
```bash
python3 -m http.server 8000 -d frontend   # http://localhost:8000
```

The page auto-detects its backend: if `window.SKILLXRAY_API_BASE` is set in `config.js`, it uses that; otherwise local HTTP dev uses `http://localhost:8080`. The public site (`keerthi166.github.io/SkillXRay`) shows a setup notice and disables scans until a backend is configured — it never assumes a local server.

## Three scan modes

`index.html` supports three modes; `analyzer.js` drives Modes 1 and 2 client-side:

- **Mode 1 (in-browser WebLLM)** — uses compact prompts (`EXTRACT_COMPACT`, `JUDGE_COMPACT`) because in-browser models have ~4k context; caps at 36 judged moves; batches judgment in groups of 6.
- **Mode 2 (user's API key)** — OpenAI or Anthropic; runs full prompts (`EXTRACT_PROMPT`, `JUDGE_PROMPT`) with 6 few-shot demos; one judge call for all moves.
- **Mode 3 (local backend)** — delegates to `localhost:8080`; full Python pipeline via the private repo.

## `analyzer.js` is auto-generated

**Do not edit `analyzer.js` by hand.** It is generated from prompt source files in the private `SkillAppropriateness` repo:

```bash
# Requires the private backend repo to be checked out
export SKILLXRAY_CODE_ROOT=/path/to/code/SkillAppropriateness
python3 frontend/scripts/build_analyzer.py
```

The script reads `prompts/layer1_phase1_read/{find_data_moves,check_privacy_violation,label_harm}.md` and `bench/agents/demos/shared/judge_demos.py`, composes the merged judge template (mirroring `merged_judge.py`), converts `{placeholder}` to `@@TOKEN@@` form, and emits them as JSON-stringified JS constants. The runtime pipeline at the bottom of the file is hand-written directly in `build_analyzer.py`.

## Rebuilding the findings snapshot

```bash
python3 frontend/scripts/build_findings.py /path/to/results_skillxray
```

The builder reads `_manifest64_summary.json` and per-skill `step4_harm.json` files, asserts move/violation counts match the manifest, strips absolute machine paths, and writes `findings-data.json`. Run the dev server to test the snapshot (the page fetches it via HTTP).

## Backend API (expected at `localhost:8080` or configured base URL)

- `POST /scan` — submit a URL; returns `{scan_id}`
- `POST /scan/upload` — submit a folder as multipart form data; returns `{scan_id}`
- `POST /scan/{id}/cancel` — cancel in-progress scan
- `GET /status/{id}` — poll for progress (`{status, step, error}`)
- `GET /card/{id}` — result card as JSON
- `GET /card/{id}/html` — result card as rendered HTML (shown in sandboxed iframe)

## Deployment

Pushing to `main` auto-deploys to `https://keerthi166.github.io/SkillXRay/`.

For a deployed backend: set `window.SKILLXRAY_API_BASE` in `frontend/config.js` and add the Pages URL to the backend's `SKILLXRAY_CORS_ORIGINS`. For local development, add `http://localhost:8000` to the backend's CORS origins.

If the Pages workflow fails on `configure-pages` with a permissions error: Settings → Pages → Source: **GitHub Actions**.

## Key design constraints

- API keys are never saved to browser storage; they are cleared after acceptance and on provider switch.
- Scan access tokens live only in memory; reports must be downloaded before leaving the tab.
- The example card in the page is curated, not generated — don't change its claims without re-checking the source at commit `9883313adaf311c03d5bda7766d9e0dbf2fd1a13` in the backend corpus.
- The findings snapshot (`findings-data.json`) is labeled preliminary; counts include a known xlsx false-positive cluster documented in the notes field.
- Valid skill folder uploads require `SKILL.md` at the top level and must be under 5 MB of analyzable content; binary and dotfile extensions are skipped (mirrors `SKIP_EXTENSIONS` in backend `fetcher.py`).
