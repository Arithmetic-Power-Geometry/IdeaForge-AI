# IdeaForge AI v1.0.0 - Final Software QA Report

## DPT-formula alignment

- Formal raw Discovery Complexity is represented as the infimum over a declared admissible procedure set. For the finite set supported by the application, the infimum is computed exactly as the minimum scalarized procedure cost.
- Each procedure cost is recorded first as the six-component vector: time, conceptual distance, search, experiment, compute, and coordination. Equal weights and a_D=24 reproduce the worked case.
- Signed representational change is `Delta L = L(R) - L(Rq)`.
- Raw Question Compression equals `Delta L` only for compression-explanatory questions. Normalized QC uses the declared scale a_Q; the default is a_Q=L(R).
- If `L(Rq) > L(R)`, the record is retained as representational expansion but excluded from the nonnegative Discovery Plane, including region, frontier, utility, and DPT-dependent venture calculations.
- Questions with no admissible declared procedure have raw DC=+infinity and are likewise excluded from the finite plane.
- Dominance, coordinate equivalence, frontier extraction, region rules, and regularized utility are applied only to plane-eligible records.

## Interaction model

- One top-level radio control selects **AI-assisted automatic** or **Manual expert** mode.
- One six-stage wizard drives Setup -> Questions -> Scoring -> Portfolio -> Startup Studio -> Export evidence.
- AI mode generates the complete requested question set before batch preliminary scoring.
- Manual mode supports anchored popover help for every 0-4 component and an advanced finite admissible-procedure set.
- Manual forms display live raw DC, normalized DC, signed change, raw QC, normalized QC, selected minimum-cost procedure, and expansion exclusion status.
- The public sidebar contains only the worked energy-case loader; there is no public six-question development-portfolio loader.

## Export and workflow verification

- Portfolio CSV export is generated from the analyzed DataFrame.
- Portfolio JSON accepts list records or DataFrame-like records and returns UTF-8 JSON bytes.
- Per-question PDF export receives the analyzed result row and readiness dictionary with consistent argument order.
- GitHub Actions installs dependencies, runs tests and reproduction, syntax-checks Python, refreshes checksums, builds a non-empty reproducibility ZIP, and uploads it with `actions/upload-artifact@v4`.

## Executed verification

- **31/31 automated tests passed**.
- Deterministic reproduction passed.
- Reproduction output: 6 archived development/test questions, 5 frontier questions, 6 coordinate classes, 196 sensitivity settings.
- Worked energy q3 reproduced as raw DC=18, normalized DC=0.750, raw QC=32, normalized QC=0.800, Region IV, Frontier=True, utility=0.425, venture-readiness=79.0.
- Expansion exclusion, inaccessible-question handling, finite-procedure infimum, raw/normalized coordinate separation, JSON export, PDF wiring, mode routing, energy loader, and artifact workflow are covered by automated tests.
- Python compilation passed for the Streamlit app, package modules, and scripts.

## Environment boundary

The build container does not include Streamlit, so a live browser-server launch was not performed. The app source is syntax-valid, the underlying calculation and export functions were executed, and the full automated test/reproduction suite passed. Streamlit Community Cloud installs the declared requirements before launch.
