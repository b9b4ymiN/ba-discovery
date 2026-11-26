# Visual discovery foundation — draft integration

Approved architectural direction: derived, standalone offline HTML; no new skill or phase; Pele diagram engine; existing Project Brain and approval gates unchanged. Phase 02 integrates Understand, Requirements and Design; wireframes, dedicated change review and final report remain later increments.

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

The Phase 01 Chromium CI passed at commit 08cfd66. Phase 02 requires a new green run and live agent evaluation; this is not a cross-browser or semantic validation claim.

## Phase 02 input (v2)

Use this shape for the three integrated skills. V1 diagram-only input remains accepted for compatibility. Source paths are explicit project-relative files (including brownfield source/docs); symlinks, hidden files other than .ba, credential extensions and paths outside the project are rejected. Only file hashes and declared references enter the artifact; do not put secrets in any visual field.

    {
      "schema_version": 2,
      "title": "Allocation planner",
      "phase": "REQUIREMENTS",
      "summary": "Review one candidate decision",
      "focus_id": "material-shortage",
      "visuals": [
        {
          "visual_id": "material-shortage",
          "title": "Shortage rule",
          "question": "What happens when material is unavailable?",
          "intent": "condition",
          "kind": "decision_table",
          "selection_reason": "Conditions and outcomes are the decision.",
          "level": "L1",
          "status": "PROPOSED",
          "source_paths": [".ba/PROJECT.md"],
          "references": [],
          "columns": ["Condition", "Candidate outcome"],
          "rows": [["Available", "Check capacity"], ["Shortage", "Open decision"]],
          "open_questions": ["Skip or partially allocate?"],
          "change_summary": "Initial proposal"
        }
      ]
    }

The selection matrix defines the intent/kind pairs. Diagrams use source instead of columns/rows. Status is required; approved-source views require an approved snapshot and canonical references but human scope review remains mandatory. Use --update with a newly reviewed focus_id to replace existing IDs and retain other views with their original source fingerprints. Optional remove_ids deletes obsolete views from the generated workspace, not Project Brain. Older phases and missing/changed source bytes are labeled STALE. The --check command reports stale and unverifiable views; it cannot detect undeclared semantic changes or watch files in the browser. Regenerate before reliance.

The GitHub CI prepares a pinned bundle, executes browser checks and uploads the package lock and bundle/license as a verification artifact. This artifact is not yet a committed vendor asset; the reviewed release packaging and cross-browser checks remain separate gates. Do not silently download at BA runtime. For visual selection behavior, use the normalized run scenarios and semantic review; fixture tests do not prove actual live agent behavior.
