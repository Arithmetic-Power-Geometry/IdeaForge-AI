# IdeaForge AI v1.0.0

**Auditable research-question generation, Discovery Plane analysis, and research-to-startup decision support.**

IdeaForge AI provides one professional six-stage workflow with a radio selector for **AI-assisted automatic** or **Manual expert** analysis. Both modes preserve provenance, keep Discovery Plane Theory (DPT) quantities separate from commercialization judgments, and end with portfolio comparison, Startup Studio, and auditable exports.

## Core workflow

1. **Setup** - choose analysis mode and declare the question-set context.
2. **Questions** - create or review the full candidate set before scoring.
3. **Scoring** - automatically estimate all selected questions or complete expert/manual forms with anchored help.
4. **Portfolio** - compute DC, QC, signed change, regions, dominance, frontier, coordinate classes, utility, venture screen, and sensitivity.
5. **Startup Studio** - document the problem, solution, users, payer, MVP, pilot KPIs, revenue, costs, partners, and risk hypotheses.
6. **Export evidence** - download portfolio CSV/JSON and per-question PDF assessments.

### AI-assisted automatic mode

The user first enters the **number of questions**, topic/keyword/problem, domain, generation goal, and novelty orientation. IdeaForge generates the entire question set before any scoring occurs. Questions can be edited or excluded, then every retained question is scored together using the transparent bundled estimator. If an OpenAI key is configured, optional LLM suggestions can be used. All estimates remain editable and must be explicitly accepted.

### Manual expert mode

The user first declares the number and wording of questions. Each retained question then receives a complete manual form. Every six-component DC input and every commercialization input has an in-app help popover explaining the 0-4 scale. A separate representation-help popover explains `L(R)` and `L(Rq)`. Live raw DC, normalized DC, signed change, raw QC, normalized QC, and Discovery-Plane eligibility are shown while scoring. Manual mode also supports a finite set of alternative admissible procedures; the minimum declared scalarized procedure cost implements the DPT infimum on that finite set.

## Worked energy case

The sidebar contains one demonstration loader: **Load worked energy case**. It loads only q1-q4 and internally verifies the published worked values before displaying the portfolio. In particular, q3 has raw DC=18, normalized DC=0.750, raw QC=32, normalized QC=0.800, Region IV, frontier membership, U0.5=0.425, and venture screen 79.0.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Streamlit Community Cloud

1. Upload the repository contents to GitHub.
2. Create a Streamlit app from the repository.
3. Set the main file path to `app/streamlit_app.py`.
4. Deploy.

The app works without an API key. For optional live LLM suggestions, set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` in Streamlit secrets. Never commit `.streamlit/secrets.toml`.

## Reproduce and test

```bash
pytest -q
python scripts/reproduce.py
python -m py_compile app/streamlit_app.py src/ideaforge/*.py scripts/*.py
python scripts/make_checksums.py
```

The GitHub Actions workflow performs these checks on push, pull request, and manual dispatch, builds `IdeaForge-AI-v1.0.0-reproducibility-artifact.zip`, verifies that it is non-empty, and uploads it with `actions/upload-artifact@v4`.

## Scientific boundary

IdeaForge does **not** infer objective DPT coordinates from a sentence alone. Formal raw DC is the infimum of declared admissible procedure cost; for the finite procedure set implemented here, this is the minimum scalarized cost. Raw QC is L(R)-L(Rq) only for compression-explanatory questions. Normalized coordinates use declared scales (defaults: a_D=24 under equal 0-4 weights and a_Q=L(R)). Representational expansion is retained with signed ΔL but excluded from the nonnegative Discovery Plane. AI estimates are preliminary. Region IV, frontier membership, utility, and venture-readiness scores do not establish truth, novelty, ethics, safety, patentability, product-market fit, funding, investment readiness, or startup success.

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.

© 2026 Mohammad Amir Khusru Akhtar.
