# SkillXray frontend

The landing page and scanner are in `index.html`, with no framework or build step.
The scanner supports URL and folder inputs, provider/model selection, a masked
API-key field, connection testing, progress, cancellation, and private reports.

## Point the site at the backend

Set `config.js` before publishing:

```javascript
window.SKILLXRAY_API_BASE = "https://YOUR-BACKEND-HOST";
```

Use the actual HTTPS address of the deployed SkillAppropriateness container. No
credentials belong in this file. Set the backend's `SKILLXRAY_CORS_ORIGINS` to
`https://keerthi166.github.io` for the existing GitHub Pages site.

An empty string selects a backend on the same origin. With no setting, local
HTTP development uses `http://localhost:8080` (same-origin on port 8080). The public
site shows a setup notice and disables scans until a backend address is configured;
it never assumes the visitor has a local server installed.

## Providers and credentials

OpenAI and Anthropic are available by default. LiteLLM appears only when the
backend advertises operator-approved gateway URLs. An internal backend can also
advertise its configured server connection; public containers hide this option.

Users select a provider and model, paste a key, optionally test the connection,
and start the scan. The key is cleared after acceptance and is never saved to
browser storage. Switching providers clears it too. The service encrypts queued
keys and uses each key only for its associated scan. Model usage is billed by the
provider. Connection testing performs a model lookup, not a full analysis.

Scan access tokens stay in memory and are sent in authorization headers, never
URLs. Refreshing or closing the tab loses access to the scan. Users can download
reports before leaving; server access expires after 24 hours. Reports display in
a sandboxed iframe.

## Develop and publish

Run `python3 -m http.server 8000 -d frontend` from the frontend repository, along
with the backend container on port 8080. Add `http://localhost:8000` to the backend
CORS origins for that local preview. The existing GitHub Actions workflow deploys
`frontend/` to GitHub Pages on pushes to `main`.

The backend's `deploy/VISITOR-SCANS.md` describes its deployment, key lifecycle,
limits, and retention. The frontend alone cannot perform the Python analysis.

## Homepage and example

The homepage uses a Liberty-inspired seafoam, black, white, and copper palette,
with responsive layouts and automatic dark-mode colors. Links to `#scanner`,
`#example`, and `#research` support direct navigation and browser history.

The example is embedded in the page and needs no backend or API key. It is a
curated source review, not an unedited generated report. It distinguishes the
session summarizer's default agent workflow from its documented optional
Anthropic API fallback. Evidence comes from `SKILL.md` and
`scripts/summarize_session.py` (lines 92–114) in the backend corpus at commit
`9883313adaf311c03d5bda7766d9e0dbf2fd1a13`, under
`corpus/glebis_claude-skills/coaching-session-summarizer/`.
Recheck that source context before changing example claims. Provider
authentication alone is not evidence of credential theft.

Supporting code and research details use native expandable disclosures. The
existing pilot metrics remain labeled preliminary; they are not performance
guarantees. Live scans still require a configured, running backend.

## Threat reports tab

`#reports` is a read-only showcase of the documented August 13, 2026 corpus run.
It uses `findings-data.json`: 54 analyzed skills, 39 with potential violations,
307 flags, and 2,336 data moves. Categories rank by affected skills, while
individual reports sort by total flags. Search, category, and finding-status
filters let visitors explore the recorded evidence. No upload or API key is needed.

The snapshot is reconciled against `_manifest64_summary.json` and the 54 referenced
`step4_harm.json` files. Six other result folders are explicitly excluded to avoid
mixing separate results with the documented run. Original absolute machine paths,
logs, and provider configuration are not exported. Evidence is rendered as text.

The data contains no severity rating; the page displays “not assessed.” Verdict
confidence is shown separately. The original counts include the known xlsx
false-positive cluster. Notes preserve that issue and the source-review context
for the coaching-session-summarizer fallback. These are automated potential
violations, not confirmed incidents or marketplace-wide prevalence.

To rebuild the snapshot after replacing or updating that documented run:

```sh
python3 frontend/scripts/build_findings.py /path/to/results_skillxray
```

The builder checks per-skill and aggregate counts before writing the snapshot.
Review the displayed run date and editorial context when importing a different run.
Serve the frontend over HTTP for the JSON fetch, using the development command above.

### Privacy Harms browsing

The showcase pins five fixed skills from the August 13 run by total flagged
moves: telegram-telethon, xlsx, daydream, thinking-patterns, and telegram. The
remaining 49 are in a collapsed browser with search and filters. Filtering does
not change the featured five. The xlsx review note remains within its report.

Each selected harm category has a two-sentence general explanation, adapted
from the Solove taxonomy summary at
https://law.shu.edu/documents/taxonomy-privacy.pdf. Inference is explicitly
identified as SkillXray's extension. The page no longer includes the run-scope
accordion or the introductory description beneath its main heading.

The general harm explanations now appear beside “Most common harm categories.”
Category buttons update the persistent definition panel on pointer hover, keyboard
focus, or click/tap. Secondary Use is selected initially. The Browse section's
category dropdown filters reports only; it no longer contains a definition box.
