from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ideaforge import (
    QuestionRecord,
    analyse_records,
    generate_questions,
    guided_estimate,
    openai_estimate,
    DC_GUIDE,
    VENTURE_GUIDE,
    DC_COMPONENTS,
    readiness_stage,
    sensitivity_grid,
    assessment_pdf,
    portfolio_json,
    load_worked_energy_case,
    discovery_complexity,
    normalized_discovery_complexity,
    question_compression,
    normalized_question_compression,
    signed_change,
    discovery_plane_eligible,
    procedure_costs,
    selected_procedure,
)

st.set_page_config(
    page_title="IdeaForge AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Optional OpenAI secret. The application remains fully usable without it.
try:
    if st.secrets.get("OPENAI_API_KEY"):
        os.environ.setdefault("OPENAI_API_KEY", str(st.secrets["OPENAI_API_KEY"]))
    if st.secrets.get("OPENAI_MODEL"):
        os.environ.setdefault("OPENAI_MODEL", str(st.secrets["OPENAI_MODEL"]))
except Exception:
    pass

st.markdown(
    """
<style>
.block-container{padding-top:1rem;max-width:1500px}
.hero{padding:1.5rem 1.7rem;border-radius:24px;background:linear-gradient(125deg,#161B33 0%,#4032A6 48%,#7659F7 100%);color:white;margin-bottom:.9rem;box-shadow:0 16px 40px rgba(63,49,166,.18)}
.hero h1{font-size:2.55rem;margin:0}.hero p{font-size:1.02rem;opacity:.93;margin:.28rem 0 0}
.card{background:white;border:1px solid #e8eaf2;border-radius:18px;padding:1rem 1.1rem;box-shadow:0 4px 14px rgba(20,25,50,.04)}
.pill{display:inline-block;padding:.34rem .65rem;border-radius:999px;background:#f0edff;color:#4538b7;font-weight:700;font-size:.82rem;margin-right:.3rem}
.small{font-size:.86rem;color:#687087}.muted{color:#697386}.green{color:#087f5b;font-weight:700}.warn{color:#a15c00;font-weight:700}
.step{border:1px solid #e7e8f1;border-radius:16px;padding:.8rem 1rem;background:#fbfbfe}
.footer{margin-top:2rem;padding:1.15rem 0 .4rem;border-top:1px solid #ececf4;text-align:center;color:#687087;font-size:.82rem}
</style>
<div class="hero"><h1>✨ IdeaForge AI</h1><p>Auditable research-question generation, Discovery Plane analysis, and research-to-startup decision support.</p></div>
""",
    unsafe_allow_html=True,
)

DOMAINS = [
    "General", "Medicine", "Computer Science", "Engineering", "Management",
    "Education", "Agriculture", "Environment", "Forensics", "Mathematics",
]
MODES = ["AI-assisted automatic", "Manual expert"]
STEP_LABELS = {
    1: "Setup",
    2: "Questions",
    3: "Scoring",
    4: "Portfolio",
    5: "Startup Studio",
    6: "Export evidence",
}

# ---------------------------- Session state ----------------------------
def init_state() -> None:
    defaults = {
        "mode": MODES[0],
        "step": 1,
        "records": [],
        "generated": [],
        "question_rows": [],
        "ai_rows": [],
        "manual_count": 3,
        "selected_startup_id": None,
        "startup_fields": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def reset_workflow(keep_mode: bool = True) -> None:
    mode = st.session_state.mode if keep_mode else MODES[0]
    for key in [
        "records", "generated", "question_rows", "ai_rows", "selected_startup_id",
        "startup_fields", "topic", "domain", "goal", "novelty", "n_questions",
        "background", "resources", "market_context",
    ]:
        st.session_state.pop(key, None)
    st.session_state.mode = mode
    st.session_state.step = 1
    init_state()


def go_step(step: int) -> None:
    st.session_state.step = max(1, min(6, int(step)))


def _plain(v):
    return v.item() if hasattr(v, "item") else v


# ---------------------------- Help popovers ----------------------------
def dc_help(key: str) -> None:
    title, description, anchors = DC_GUIDE[key]
    with st.popover("❓ Help", use_container_width=True):
        st.markdown(f"**{title}**")
        st.write(description)
        st.dataframe(
            pd.DataFrame({"Score": list(range(5)), "Interpretation": anchors}),
            hide_index=True,
            use_container_width=True,
        )


def venture_help(key: str) -> None:
    title, anchors = VENTURE_GUIDE[key]
    with st.popover("❓ Help", use_container_width=True):
        st.markdown(f"**{title}**")
        st.write("This is a commercialization judgment, not a DPT construct and not a probability of startup success.")
        st.dataframe(
            pd.DataFrame({"Score": list(range(5)), "Interpretation": anchors}),
            hide_index=True,
            use_container_width=True,
        )


def representation_help() -> None:
    with st.popover("❓ Representation help", use_container_width=True):
        st.markdown("**Formal DPT representation quantities**")
        st.write(
            "L(R) is the declared description length before the question reorganizes the Reality Space; "
            "L(Rq) is the description length after the question-induced representation. Use one coding language consistently."
        )
        st.markdown(
            "- Signed change: ΔL = L(R) - L(Rq).\n"
            "- If L(Rq) ≤ L(R), raw QC = ΔL and the question is compression-explanatory.\n"
            "- The app reports normalized QC = raw QC / a_Q, using a_Q=L(R) unless another declared scale is supplied.\n"
            "- If L(Rq) > L(R), ΔL is retained as representational expansion, but the question is excluded from the nonnegative Discovery Plane."
        )
        st.info("Worked energy example: L(R)=40, L(Rq)=8, raw QC=32, a_Q=40, normalized QC=0.800.")


def procedure_help() -> None:
    with st.popover("❓ Procedure / DC help", use_container_width=True):
        st.markdown("**Formal DPT Discovery Complexity**")
        st.write(
            "DPT defines DC as the infimum of procedure cost over admissible question-generating procedures. "
            "For the finite procedure set declared in IdeaForge, the infimum is the minimum scalarized procedure cost."
        )
        st.markdown(
            "The default cost vector has six 0–4 components: time, conceptual distance, search, experiment, compute, and coordination. "
            "With equal weights, raw procedure cost is their sum and normalized DC divides the minimum by a_D=24."
        )
        st.warning("If no admissible procedure exists, formal DC is +∞ and the question is not assigned a finite Discovery-Plane coordinate.")


def show_progress() -> None:
    cols = st.columns(6)
    current = st.session_state.step
    for i, col in enumerate(cols, 1):
        if i == current:
            col.markdown(f"**{i}. {STEP_LABELS[i]}**")
        elif i < current:
            col.markdown(f"✅ {i}. {STEP_LABELS[i]}")
        else:
            col.markdown(f"○ {i}. {STEP_LABELS[i]}")
    st.divider()


# ---------------------------- Data helpers ----------------------------
def validate_and_store(payloads: list[dict]) -> tuple[bool, str]:
    records = []
    ids = set()
    try:
        for payload in payloads:
            qid = str(payload.get("question_id", "")).strip()
            if not qid:
                raise ValueError("Every question requires a unique question ID.")
            if qid in ids:
                raise ValueError(f"Duplicate question ID: {qid}")
            ids.add(qid)
            records.append(QuestionRecord(**payload).to_dict())
    except Exception as exc:
        return False, str(exc)
    st.session_state.records = records
    return True, f"Stored {len(records)} auditable question records."


def result_frame(tau_d: float, tau_q: float, lam: float) -> pd.DataFrame:
    if not st.session_state.records:
        return pd.DataFrame()
    records = [QuestionRecord(**r) for r in st.session_state.records]
    return analyse_records(records, tau_d, tau_q, lam)


def load_energy_case() -> None:
    payloads = load_worked_energy_case(ROOT / "data" / "worked_energy_case.csv")
    records = [QuestionRecord(**p) for p in payloads]
    check = analyse_records(records, 0.65, 0.65, 0.50)
    q3 = check.loc[check.question_id == "q3"].iloc[0]
    if not (
        round(float(q3.dc), 3) == 0.750
        and round(float(q3.qc), 3) == 0.800
        and str(q3.region) == "IV"
        and bool(q3.frontier)
    ):
        raise ValueError("Worked energy case failed internal validation.")
    st.session_state.records = [r.to_dict() for r in records]
    st.session_state.mode = "Manual expert"
    st.session_state.mode_radio = "Manual expert"
    st.session_state.question_rows = [
        {"question_id": r.question_id, "question": r.question, "include": True}
        for r in records
    ]
    st.session_state.step = 4
    st.session_state.flash = "Worked energy case loaded successfully: q1-q4."


def build_auto_rows(questions: list[dict], domain: str, background: str, resources: str, market_context: str, use_live_ai: bool) -> list[dict]:
    rows = []
    for item in questions:
        q = str(item["question"]).strip()
        estimate = None
        source = "Transparent guided estimator"
        if use_live_ai and os.getenv("OPENAI_API_KEY"):
            estimate = openai_estimate(q, domain, background, resources, market_context)
            if estimate:
                source = "Optional LLM suggestion"
        if not estimate:
            estimate = guided_estimate(q, domain, background, resources, market_context)
        row = {
            "question_id": str(item.get("id") or f"G{len(rows)+1}"),
            "question": q,
            "architecture": str(item.get("architecture", "Generated")),
            "domain": domain,
            "keyword": str(st.session_state.get("topic", "")),
            "origin": "Generated",
            "scoring_mode": "AI-assisted",
            "estimate_source": source,
            **estimate,
        }
        rows.append(row)
    return rows


def auto_rows_to_payloads(rows: list[dict]) -> list[dict]:
    allowed = set(QuestionRecord.__dataclass_fields__)
    payloads = []
    for row in rows:
        payload = {k: _plain(v) for k, v in row.items() if k in allowed}
        payload["rationale"] = str(row.get("rationale", "Preliminary estimate reviewed by user."))
        payload["confidence"] = str(row.get("confidence", "Moderate"))
        payloads.append(payload)
    return payloads


def manual_seed_rows(n: int, domain: str, topic: str) -> list[dict]:
    prior = st.session_state.get("question_rows", [])
    if len(prior) == n:
        return prior
    return [
        {
            "question_id": f"M{i}",
            "question": "",
            "include": True,
            "domain": domain,
            "keyword": topic,
        }
        for i in range(1, n + 1)
    ]


def startup_template(question: str, domain: str) -> dict:
    return {
        "Problem": f"Define the measurable user or institutional pain addressed by: {question}",
        "Proposed solution": "Describe the smallest product or decision-support capability that could test the opportunity.",
        "Target users": "Who uses the product or workflow directly?",
        "Paying customer": "Who controls budget or procurement?",
        "Value proposition": "What measurable improvement would justify adoption?",
        "Existing alternatives": "Current manual process, incumbent software, or non-consumption alternative.",
        "Differentiation hypothesis": "Why might this approach outperform or complement current alternatives?",
        "Required data": "List the minimum data needed for a pilot.",
        "Core technology": f"Specify the minimum technical stack appropriate to {domain}.",
        "MVP": "Build the smallest auditable prototype that tests one critical assumption.",
        "Pilot KPIs": "Define measurable technical, user, economic, safety, and adoption outcomes.",
        "Revenue options": "Subscription, implementation fee, service contract, licensing, or performance-linked model as appropriate.",
        "Cost drivers": "Data, compute, integration, deployment, support, compliance, and customer acquisition.",
        "Partners": "Identify domain, data, implementation, channel, and validation partners.",
        "IP / regulatory / ethics": "Assess IP ownership, privacy, security, safety, regulatory, bias, and ethical obligations before commercialization.",
    }


# ---------------------------- Sidebar ----------------------------
with st.sidebar:
    st.header("Analysis settings")
    tau_d = st.slider("DC region threshold", 0.0, 1.0, 0.65, 0.05)
    tau_q = st.slider("QC region threshold", 0.0, 1.0, 0.65, 0.05)
    lam = st.slider("Utility cost penalty λ", 0.0, 2.0, 0.50, 0.05)
    st.caption("Defaults reproduce the worked-guide convention. Thresholds are analytical choices, not natural laws.")
    st.divider()
    if st.button("Load worked energy case", use_container_width=True):
        try:
            load_energy_case()
            st.rerun()
        except Exception as exc:
            st.error(f"Could not load worked energy case: {exc}")
    if st.button("Reset workflow", use_container_width=True):
        reset_workflow(keep_mode=True)
        st.rerun()
    st.divider()
    st.caption("IdeaForge AI v1.0.0")
    st.caption("Apache License 2.0")

# ---------------------------- Mode and progress ----------------------------
st.subheader("Choose analysis mode")
if "mode_radio" not in st.session_state:
    st.session_state.mode_radio = st.session_state.mode

def _mode_changed() -> None:
    st.session_state.mode = st.session_state.mode_radio
    reset_workflow(keep_mode=True)

st.radio(
    "Mode",
    MODES,
    horizontal=True,
    key="mode_radio",
    on_change=_mode_changed,
    help="AI-assisted automatic generates and preliminarily scores all selected questions. Manual expert requires the user to declare every score and representation value.",
)

flash = st.session_state.pop("flash", None)
if flash:
    st.success(flash)

show_progress()
mode = st.session_state.mode
step = st.session_state.step

# ---------------------------- STEP 1: Setup ----------------------------
if step == 1:
    st.header("Step 1 - Define the question set")
    if mode == "AI-assisted automatic":
        st.info("Enter the number of questions first, then the topic and domain. IdeaForge generates the complete candidate set before any scoring begins.")
        c1, c2, c3 = st.columns([1, 2, 2])
        n = c1.number_input("Number of questions to generate", 1, 10, int(st.session_state.get("n_questions", 5)), 1)
        topic = c2.text_input("Topic / keyword / problem", value=st.session_state.get("topic", ""), placeholder="e.g., student dropout")
        domain = c3.selectbox("Domain", DOMAINS, index=DOMAINS.index(st.session_state.get("domain", "General")))
        c4, c5 = st.columns(2)
        goal = c4.selectbox("Generation goal", ["Balanced", "Startup opportunity", "Scientific discovery", "Social impact"])
        novelty = c5.selectbox("Novelty orientation", ["Moderate", "High"])
        st.markdown("##### Optional context")
        c6, c7, c8 = st.columns(3)
        background = c6.text_area("Available background knowledge", value=st.session_state.get("background", ""), height=90)
        resources = c7.text_area("Available data / resources", value=st.session_state.get("resources", ""), height=90)
        market_context = c8.text_area("Market / user context", value=st.session_state.get("market_context", ""), height=90)
        if st.button("Generate all candidate questions →", type="primary", use_container_width=True):
            if not topic.strip():
                st.error("Enter a topic, keyword, or problem before generating questions.")
            else:
                st.session_state.n_questions = int(n)
                st.session_state.topic = topic.strip()
                st.session_state.domain = domain
                st.session_state.goal = goal
                st.session_state.novelty = novelty
                st.session_state.background = background
                st.session_state.resources = resources
                st.session_state.market_context = market_context
                generated = generate_questions(topic.strip(), domain, int(n), goal, novelty)
                for item in generated:
                    item["include"] = True
                    item["domain"] = domain
                    item["keyword"] = topic.strip()
                st.session_state.generated = generated
                st.session_state.step = 2
                st.rerun()
    else:
        st.info("Manual expert mode evaluates a declared set of questions. Every score is explained before entry, and all values remain editable.")
        c1, c2, c3 = st.columns([1, 2, 2])
        n = c1.number_input("Number of questions to evaluate", 1, 10, int(st.session_state.get("manual_count", 3)), 1)
        topic = c2.text_input("Topic / project label (optional)", value=st.session_state.get("topic", ""))
        domain = c3.selectbox("Domain", DOMAINS, index=DOMAINS.index(st.session_state.get("domain", "General")))
        if st.button("Create manual question forms →", type="primary", use_container_width=True):
            st.session_state.manual_count = int(n)
            st.session_state.topic = topic.strip()
            st.session_state.domain = domain
            st.session_state.question_rows = manual_seed_rows(int(n), domain, topic.strip())
            st.session_state.step = 2
            st.rerun()

# ---------------------------- STEP 2: Questions ----------------------------
elif step == 2:
    st.header("Step 2 - Review the complete question set")
    if mode == "AI-assisted automatic":
        if not st.session_state.generated:
            st.warning("No generated questions are available. Return to Step 1.")
        else:
            df = pd.DataFrame(st.session_state.generated)
            display = df[["include", "id", "architecture", "question"]].copy()
            edited = st.data_editor(
                display,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "include": st.column_config.CheckboxColumn("Analyze", default=True),
                    "id": st.column_config.TextColumn("ID", disabled=True),
                    "architecture": st.column_config.TextColumn("Architecture", disabled=True),
                    "question": st.column_config.TextColumn("Research question", width="large"),
                },
                key="generated_editor",
            )
            st.caption("All questions are generated first. You may edit wording or deselect a question before automatic preliminary scoring.")
            b1, b2 = st.columns(2)
            if b1.button("← Back", use_container_width=True):
                go_step(1); st.rerun()
            if b2.button("Next: automatically score selected questions →", type="primary", use_container_width=True):
                selected = []
                for _, row in edited.iterrows():
                    if bool(row["include"]):
                        selected.append({
                            "id": str(row["id"]),
                            "architecture": str(row["architecture"]),
                            "question": str(row["question"]),
                        })
                if not selected:
                    st.error("Select at least one question.")
                else:
                    use_live_ai = bool(os.getenv("OPENAI_API_KEY"))
                    st.session_state.ai_rows = build_auto_rows(
                        selected,
                        st.session_state.domain,
                        st.session_state.get("background", ""),
                        st.session_state.get("resources", ""),
                        st.session_state.get("market_context", ""),
                        use_live_ai,
                    )
                    st.session_state.step = 3
                    st.rerun()
    else:
        rows = st.session_state.question_rows
        df = pd.DataFrame(rows)[["question_id", "question", "include"]]
        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "question_id": st.column_config.TextColumn("Question ID", width="small"),
                "question": st.column_config.TextColumn("Research question", width="large", required=True),
                "include": st.column_config.CheckboxColumn("Evaluate", default=True),
            },
            key="manual_question_editor",
        )
        b1, b2 = st.columns(2)
        if b1.button("← Back", use_container_width=True):
            go_step(1); st.rerun()
        if b2.button("Next: enter manual scoring →", type="primary", use_container_width=True):
            selected = []
            seen = set()
            for _, row in edited.iterrows():
                if not bool(row["include"]):
                    continue
                qid = str(row["question_id"]).strip()
                q = str(row["question"]).strip()
                if not qid or not q:
                    st.error("Every selected row needs a question ID and question text.")
                    st.stop()
                if qid in seen:
                    st.error(f"Duplicate question ID: {qid}")
                    st.stop()
                seen.add(qid)
                selected.append({"question_id": qid, "question": q, "include": True})
            if not selected:
                st.error("Select at least one question.")
            else:
                st.session_state.question_rows = selected
                st.session_state.step = 3
                st.rerun()

# ---------------------------- STEP 3: Scoring ----------------------------
elif step == 3:
    st.header("Step 3 - Score and review")
    if mode == "AI-assisted automatic":
        st.info("All selected questions have received preliminary automatic estimates. Review or edit them before acceptance. These are suggestions, not objective DPT measurements.")
        st.caption("If an OpenAI key is configured, the app may use that optional provider; otherwise it uses the transparent deterministic estimator bundled with the repository.")
        help1, help2 = st.columns(2)
        with help1:
            with st.popover("❓ How automatic scoring works", use_container_width=True):
                st.write("The automatic stage proposes six DC components, L(R), L(Rq), five commercialization values, confidence, and a rationale for every generated question. All values remain editable before acceptance.")
        with help2:
            representation_help()

        edited_rows = []
        for idx, row in enumerate(st.session_state.ai_rows):
            qid = row["question_id"]
            with st.expander(f"{qid} · {row.get('architecture','Generated')} · {row['question']}", expanded=(idx == 0)):
                st.caption(f"Estimate source: {row.get('estimate_source','Transparent guided estimator')} · Confidence: {row.get('confidence','Moderate')}")
                st.write(row.get("rationale", ""))
                local = dict(row)
                cols = st.columns(3)
                for j, key in enumerate(DC_COMPONENTS):
                    title = DC_GUIDE[key][0]
                    local[key] = cols[j % 3].slider(title, 0, 4, int(local.get(key, 2)), key=f"ai_{idx}_{key}")
                c1, c2 = st.columns(2)
                local["l_before"] = c1.number_input("Description length before, L(R)", min_value=0.01, value=float(local.get("l_before", 40.0)), step=1.0, key=f"ai_lb_{idx}")
                local["l_after"] = c2.number_input("Description length after, L(Rq)", min_value=0.0, value=float(local.get("l_after", 20.0)), step=1.0, key=f"ai_la_{idx}")
                local["dc_scale"] = None
                local["qc_scale"] = None
                local["admissible_procedures"] = None
                local["feasible"] = True
                dc_raw_live = sum(float(local[k]) for k in DC_COMPONENTS)
                dc_norm_live = dc_raw_live / 24.0
                delta_live = float(local["l_before"]) - float(local["l_after"])
                qc_raw_live = delta_live if delta_live >= 0 else None
                qc_norm_live = (qc_raw_live / float(local["l_before"])) if qc_raw_live is not None else None
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Raw DC", f"{dc_raw_live:.1f}")
                m2.metric("Normalized DC", f"{dc_norm_live:.3f}")
                m3.metric("Signed ΔL", f"{delta_live:.1f}")
                m4.metric("Raw QC", "N/A" if qc_raw_live is None else f"{qc_raw_live:.1f}")
                m5.metric("Normalized QC", "Excluded" if qc_norm_live is None else f"{qc_norm_live:.3f}")
                if qc_raw_live is None:
                    st.warning("Representational expansion: this record will be retained for audit but excluded from region, frontier, utility, and venture calculations.")
                st.markdown("**Commercialization screen (0-4)**")
                vcols = st.columns(5)
                for j, key in enumerate(VENTURE_GUIDE):
                    local[key] = vcols[j].slider(VENTURE_GUIDE[key][0], 0, 4, int(local.get(key, 2)), key=f"ai_v_{idx}_{key}")
                edited_rows.append(local)
        st.session_state.ai_rows = edited_rows
        b1, b2 = st.columns(2)
        if b1.button("← Back to questions", use_container_width=True):
            go_step(2); st.rerun()
        if b2.button("Accept all reviewed estimates and analyze portfolio →", type="primary", use_container_width=True):
            ok, msg = validate_and_store(auto_rows_to_payloads(st.session_state.ai_rows))
            if ok:
                st.success(msg)
                go_step(4); st.rerun()
            else:
                st.error(msg)
    else:
        st.info("Manual mode is the audit baseline. Every value has a help popover explaining what the score signifies.")
        payloads = []
        for idx, item in enumerate(st.session_state.question_rows):
            qid = item["question_id"]
            with st.expander(f"{qid} · {item['question']}", expanded=(idx == 0)):
                st.markdown("##### Discovery Complexity: declared admissible procedure set")
                procedure_help()
                st.caption("Enter the primary admissible procedure first. In the advanced panel you may declare alternatives; IdeaForge uses the minimum scalarized cost, matching the infimum on this finite declared set.")
                dc_values = {}
                for key in DC_COMPONENTS:
                    left, right = st.columns([5, 1])
                    with left:
                        dc_values[key] = st.slider(
                            DC_GUIDE[key][0], 0, 4, 2,
                            key=f"m_{idx}_{key}",
                        )
                    with right:
                        dc_help(key)
                procedures = [{"name": "P1", **dc_values}]
                with st.expander("Advanced: add alternative admissible procedures"):
                    n_proc = st.number_input("Number of admissible procedures", 1, 3, 1, 1, key=f"m_nproc_{idx}")
                    st.caption("P1 uses the primary scores above. Add P2/P3 only when you can justify distinct admissible question-generating procedures under the same cost convention.")
                    for pno in range(2, int(n_proc) + 1):
                        st.markdown(f"**Procedure P{pno}**")
                        prow = {"name": f"P{pno}"}
                        pcols = st.columns(3)
                        for j, key in enumerate(DC_COMPONENTS):
                            prow[key] = pcols[j % 3].slider(DC_GUIDE[key][0], 0, 4, 2, key=f"m_{idx}_p{pno}_{key}")
                        procedures.append(prow)
                st.markdown("##### Representation declaration")
                representation_help()
                c1, c2 = st.columns(2)
                lb = c1.number_input("Description length before question, L(R)", min_value=0.01, value=40.0, step=1.0, key=f"m_lb_{idx}")
                la = c2.number_input("Description length after reorganisation, L(Rq)", min_value=0.0, value=20.0, step=1.0, key=f"m_la_{idx}")
                procedure_raw_costs = [sum(float(proc[k]) for k in DC_COMPONENTS) for proc in procedures]
                raw_cost = min(procedure_raw_costs)
                dc_live = raw_cost / 24.0
                chosen_proc = procedures[procedure_raw_costs.index(raw_cost)]["name"]
                delta = lb - la
                qc_raw_live = delta if delta >= 0 else None
                qc_live = (qc_raw_live / lb) if qc_raw_live is not None else None
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Raw DC (infimum)", f"{raw_cost:.1f}", delta=f"best {chosen_proc}")
                m2.metric("Normalized DC", f"{dc_live:.3f}", delta="a_D=24")
                m3.metric("Signed ΔL", f"{delta:.1f}")
                m4.metric("Raw QC", "N/A" if qc_raw_live is None else f"{qc_raw_live:.1f}")
                m5.metric("Normalized QC", "Excluded" if qc_live is None else f"{qc_live:.3f}", delta="a_Q=L(R)")
                if qc_raw_live is None:
                    st.warning("L(Rq) > L(R): representational expansion is retained, but this question will be excluded from the nonnegative Discovery Plane as required by DPT.")
                st.markdown("##### Commercialization screen (0-4)")
                venture = {}
                for key in VENTURE_GUIDE:
                    left, right = st.columns([5, 1])
                    with left:
                        venture[key] = st.slider(VENTURE_GUIDE[key][0], 0, 4, 2, key=f"mv_{idx}_{key}")
                    with right:
                        venture_help(key)
                payloads.append({
                    "question_id": qid,
                    "question": item["question"],
                    **dc_values,
                    "l_before": float(lb),
                    "l_after": float(la),
                    "dc_scale": None,
                    "qc_scale": None,
                    "admissible_procedures": procedures if len(procedures) > 1 else None,
                    "feasible": True,
                    **venture,
                    "domain": st.session_state.get("domain", "General"),
                    "keyword": st.session_state.get("topic", ""),
                    "origin": "Human",
                    "scoring_mode": "Manual",
                    "confidence": "User-declared",
                    "rationale": "Manual values entered under the displayed anchored guidance.",
                })
        b1, b2 = st.columns(2)
        if b1.button("← Back to questions", use_container_width=True):
            go_step(2); st.rerun()
        if b2.button("Analyze all manual questions →", type="primary", use_container_width=True):
            ok, msg = validate_and_store(payloads)
            if ok:
                st.success(msg)
                go_step(4); st.rerun()
            else:
                st.error(msg)

# ---------------------------- STEP 4: Portfolio ----------------------------
elif step == 4:
    st.header("Step 4 - Portfolio, Discovery Plane, and sensitivity")
    res = result_frame(tau_d, tau_q, lam)
    if res.empty:
        st.warning("No analyzed records are available.")
    else:
        eligible = res[res.discovery_plane_eligible].copy()
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Submitted records", len(res))
        m2.metric("Plane-eligible", len(eligible))
        m3.metric("Frontier questions", int(eligible.frontier.sum()) if len(eligible) else 0)
        m4.metric("Unique coordinate classes", int(eligible.coordinate_class.nunique()) if len(eligible) else 0)
        top = None
        if len(eligible):
            top = eligible.sort_values(["utility", "qc"], ascending=[False, False]).iloc[0]
            m5.metric("Highest-ranked under current settings", str(top.question_id))
        else:
            m5.metric("Highest-ranked under current settings", "N/A")
        show_cols = [
            "question_id", "question", "dc_raw", "dc", "delta_l", "qc_raw", "qc",
            "discovery_plane_eligible", "region", "frontier", "coordinate_class", "utility",
            "venture_readiness", "selected_procedure", "recommendation", "next_action",
        ]
        st.dataframe(res[show_cols], hide_index=True, use_container_width=True)

        excluded = res[~res.discovery_plane_eligible]
        if len(excluded):
            st.warning(f"{len(excluded)} record(s) are retained for audit but excluded from the nonnegative Discovery Plane because of representational expansion or procedure infeasibility.")

        st.markdown("##### Discovery Plane")
        if len(eligible):
            fig, ax = plt.subplots(figsize=(8.5, 5.0))
            ax.scatter(eligible.dc, eligible.qc, s=72)
            for _, r in eligible.iterrows():
                ax.annotate(str(r.question_id), (r.dc, r.qc), xytext=(5, 5), textcoords="offset points")
            ax.axvline(tau_d, linestyle="--", linewidth=1)
            ax.axhline(tau_q, linestyle="--", linewidth=1)
            frontier = eligible[eligible.frontier].sort_values(["dc", "qc"])
            if len(frontier) > 1:
                ax.plot(frontier.dc, frontier.qc, linewidth=1.4)
            ax.set_xlim(0, max(1.05, float(eligible.dc.max()) * 1.05))
            ax.set_ylim(0, max(1.05, float(eligible.qc.max()) * 1.05))
            ax.set_xlabel("Normalized Discovery Complexity")
            ax.set_ylabel("Normalized Question Compression")
            ax.set_title("Discovery Plane portfolio")
            st.pyplot(fig, clear_figure=True)
        else:
            st.info("No record is currently eligible for a nonnegative Discovery-Plane coordinate.")

        with st.expander("Sensitivity Lab - execute a full threshold/utility grid"):
            st.write("The default audit runs 7 DC thresholds × 7 QC thresholds × 4 λ values = 196 configurations.")
            if st.button("Run 196-setting sensitivity audit", use_container_width=True):
                records = [QuestionRecord(**r) for r in st.session_state.records]
                grid = sensitivity_grid(records)
                st.session_state.sensitivity = grid.to_dict("records")
            if st.session_state.get("sensitivity"):
                grid = pd.DataFrame(st.session_state.sensitivity)
                counts = grid.top_question.value_counts().rename_axis("question_id").reset_index(name="configurations_led")
                counts["share"] = counts.configurations_led / len(grid)
                st.dataframe(counts, hide_index=True, use_container_width=True)
                st.download_button("Download sensitivity grid CSV", grid.to_csv(index=False).encode(), "sensitivity_grid.csv", "text/csv")

        b1, b2 = st.columns(2)
        if b1.button("← Back to scoring", use_container_width=True):
            go_step(3); st.rerun()
        if b2.button("Next: develop a startup hypothesis →", type="primary", use_container_width=True, disabled=(top is None)):
            st.session_state.selected_startup_id = str(top.question_id)
            go_step(5); st.rerun()

# ---------------------------- STEP 5: Startup Studio ----------------------------
elif step == 5:
    st.header("Step 5 - Startup Studio")
    res = result_frame(tau_d, tau_q, lam)
    if res.empty:
        st.warning("Analyze a portfolio first.")
    else:
        eligible = res[res.discovery_plane_eligible].copy()
        ids = eligible.question_id.astype(str).tolist()
        if not ids:
            st.warning("No Discovery-Plane-eligible question is available for Startup Studio under the current declared conventions.")
            st.stop()
        default_id = st.session_state.selected_startup_id if st.session_state.selected_startup_id in ids else ids[0]
        qid = st.selectbox("Select a question for deeper venture due diligence", ids, index=ids.index(default_id))
        st.session_state.selected_startup_id = qid
        row = res.loc[res.question_id.astype(str) == qid].iloc[0]
        payload = next(r for r in st.session_state.records if str(r["question_id"]) == qid)
        record = QuestionRecord(**payload)
        st.markdown(f"### {qid}: {row.question}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("DC", f"{row.dc:.3f}")
        c2.metric("QC", f"{row.qc:.3f}")
        c3.metric("Venture screen", f"{row.venture_readiness:.1f}/100")
        c4.metric("Frontier", "Yes" if bool(row.frontier) else "No")
        st.warning("The venture score is a transparent triage heuristic, not a probability of startup success, investment, or product-market fit.")

        st.markdown("##### Readiness evidence")
        readiness = readiness_stage(record, float(row.venture_readiness))
        st.dataframe(pd.DataFrame({"Dimension": readiness.keys(), "Status": readiness.values()}), hide_index=True, use_container_width=True)
        st.info(f"Recommended next action: {row.next_action}")

        current = st.session_state.startup_fields.get(qid) or startup_template(str(row.question), record.domain)
        st.markdown("##### Venture hypothesis worksheet")
        updated = {}
        keys = list(current.keys())
        for i in range(0, len(keys), 2):
            cols = st.columns(2)
            for j, key in enumerate(keys[i:i+2]):
                updated[key] = cols[j].text_area(key, value=current[key], height=105, key=f"startup_{qid}_{key}")
        st.session_state.startup_fields[qid] = updated

        b1, b2 = st.columns(2)
        if b1.button("← Back to portfolio", use_container_width=True):
            go_step(4); st.rerun()
        if b2.button("Next: export auditable evidence →", type="primary", use_container_width=True):
            go_step(6); st.rerun()

# ---------------------------- STEP 6: Export ----------------------------
elif step == 6:
    st.header("Step 6 - Export auditable evidence")
    res = result_frame(tau_d, tau_q, lam)
    if res.empty:
        st.warning("No analyzed records are available.")
    else:
        st.download_button("Download portfolio CSV", res.to_csv(index=False).encode("utf-8"), "ideaforge_portfolio.csv", "text/csv", use_container_width=True)
        st.download_button("Download portfolio JSON", portfolio_json(st.session_state.records), "ideaforge_portfolio.json", "application/json", use_container_width=True)
        st.markdown("##### Per-question PDF assessment")
        ids = res.question_id.astype(str).tolist()
        qid = st.selectbox("Question", ids, key="report_qid")
        payload = next(r for r in st.session_state.records if str(r["question_id"]) == qid)
        row = res.loc[res.question_id.astype(str) == qid].iloc[0].to_dict()
        record = QuestionRecord(**payload)
        readiness = readiness_stage(record, float(row["venture_readiness"])) if bool(row.get("discovery_plane_eligible")) else None
        pdf_bytes = assessment_pdf(row, readiness)
        st.download_button("Download assessment PDF", pdf_bytes, f"IdeaForge_{qid}_assessment.pdf", "application/pdf", use_container_width=True)
        if st.session_state.get("startup_fields", {}).get(qid):
            st.markdown("##### Startup Studio worksheet")
            st.dataframe(pd.DataFrame({"Field": st.session_state.startup_fields[qid].keys(), "Entry": st.session_state.startup_fields[qid].values()}), hide_index=True, use_container_width=True)
        c1, c2 = st.columns(2)
        if c1.button("← Back to Startup Studio", use_container_width=True):
            go_step(5); st.rerun()
        if c2.button("Start a new analysis", type="primary", use_container_width=True):
            reset_workflow(keep_mode=True); st.rerun()

st.markdown(
    """
<div class="footer">
<strong>IdeaForge AI v1.0.0</strong> · © 2026 Mohammad Amir Khusru Akhtar · Licensed under the Apache License 2.0<br/>
Discovery Plane Theory-based research-to-startup decision support. AI-assisted estimates remain preliminary, editable, and auditable.
</div>
""",
    unsafe_allow_html=True,
)
