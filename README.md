# frontend/ — the SkillXray frontend

The public face of the project: landing page + scanner demo, in one self-contained
`index.html` (no framework, no build step, no external assets; light & dark themes).

**Status: demo.** The "Scan a skill" page replays a *real recorded audit*
(coaching-session-summarizer). It becomes live when `backend/` ships — the swap is
~10 lines (replace the scripted log with `POST /scan` + `/status` polling).

## Run locally

```bash
open frontend/index.html            # or:
python3 -m http.server 8000 -d website   # → http://localhost:8000
```

