# Visual discovery foundation — draft integration

Approved architectural direction: derived, standalone offline HTML; no new skill or phase; Pele diagram engine; existing Project Brain and approval gates unchanged. This initial increment deliberately does not integrate the phase skills, wireframes, change review, or the fixed FRD report.

## Prepare the renderer

From the plugin root (one-time connected preparation; npm/Node is not required to open the exported HTML):

    npm install --prefix assets/visual --ignore-scripts --no-audit --no-fund

The package manifest pins Pele 1.7.0. Verify the actual package and license, then retain a reviewed package-lock.json and verified bundle as a release asset before distribution. This draft does not commit the binary/minified bundle or a verified lockfile. Do not silently substitute an unpinned release. Official API: https://pele.run/api.

## Generate

Supply a temporary JSON file (do not use it as a second canonical truth source):

    {
      "title": "Allocation workflow",
      "phase": "DESIGN",
      "summary": "Illustrative draft",
      "sources": [".ba/PROJECT.md"],
      "diagrams": [
        {
          "title": "Proposed flow",
          "description": "Illustration only; not approved",
          "source": "flowchart LR\nA[Order] --> B[Planner review]",
          "references": []
        }
      ]
    }

    python scripts/ba_visual.py --project /path/to/project --input /path/to/visual.json
    python scripts/ba_visual.py --project /path/to/project --check

Open docs/BA-Workspace.html directly. The output contains embedded JS, CSS, license and payload, no remote references, and is always labeled DRAFT. Only the derived HTML may be replaced; unrelated files are rejected. The checker verifies only declared source contents. There is no automatic file watcher or approval action. The diagram uses a static SVG image, not editable/live mount; this keeps SVG DOM inert. A future sandboxed interaction design may extend it.

## Verification before merge

- Run python -m pytest tests/ -q and python tests/validate_repo.py (the repo's documented regression commands). The Visual foundation workflow also runs tests/visual_browser_smoke.py using a real pinned Pele package and headless Chromium; a green run is required before merging this increment. Safari/iOS and Firefox remain manual verification.
- Prepare the actual pinned bundle, generate from existing example projects, test all five P0 diagram types and malformed syntax with Chrome/Edge, Firefox and Safari/iOS where available.
- Confirm offline file:// operation, zero network traffic, readable Thai labels, SVG styling, source error fallback, injection payloads, source freshness and preservation of .ba/ bytes.
- Ensure the minified bundle is safe to embed (script delimiter guard must pass); test CSP hash enforcement and rendering with actual library.
- Keep existing report, version, phase gates and behavioral evals unchanged until the next increment.

This is foundation only; no runtime browser verification or full regression claim is made by this draft.
