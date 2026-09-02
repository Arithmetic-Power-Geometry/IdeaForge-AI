from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Sequence, Any
import math

DC_COMPONENTS = ("time", "conceptual", "search", "experiment", "compute", "coordination")
VENTURE_POSITIVE = ("market_pain", "buyer_clarity", "digital_deployability", "scale_potential", "social_impact")

DC_GUIDE = {
    "time": ("Time requirement", "How much additional time is likely to be required to make and investigate the question?", ["Almost immediate / trivial additional time", "Short, bounded effort", "Moderate project duration", "Long or multi-stage investigation", "Unusually long, multi-year or highly uncertain timeline"]),
    "conceptual": ("Conceptual distance", "How far does the question move beyond the team's existing concepts and explanatory language?", ["Direct application of established concepts", "Small extension of familiar ideas", "Moderate integration or reframing", "Major cross-domain or theoretical integration", "Foundational conceptual leap with weak established guidance"]),
    "search": ("Search/literature burden", "How difficult is it to assemble the relevant prior evidence and literature?", ["Evidence is readily identifiable", "Focused literature search", "Broad but manageable review", "Fragmented multi-domain evidence search", "Very dispersed, poorly indexed or historically difficult evidence"]),
    "experiment": ("Experimental burden", "How demanding is the empirical or real-world validation required?", ["No meaningful experiment required", "Simple validation with available data/resources", "Moderate experiment or controlled study", "Substantial field deployment or specialised resources", "Very demanding, costly, long-term or unusually difficult experimentation"]),
    "compute": ("Computational burden", "How much data engineering, modelling or computation is required?", ["Negligible computation", "Routine analysis on standard hardware", "Moderate modelling / data processing", "Large-scale or specialised computation", "Unusually intensive, distributed or frontier-scale computation"]),
    "coordination": ("Coordination burden", "How much coordination across people, units or institutions is required?", ["Individual work", "Small local team", "Several roles or one institutional unit", "Multiple teams/stakeholders or sites", "Extensive multi-institutional, regulatory or ecosystem coordination"]),
}

VENTURE_GUIDE = {
    "market_pain": ("Market/problem pain", ["No demonstrated problem", "Weak inconvenience", "Meaningful but non-urgent pain", "Strong recurring pain with visible consequences", "Critical, costly or strategically urgent pain"]),
    "buyer_clarity": ("Buyer/user clarity", ["No identifiable user/buyer", "Potential users unclear", "User known but payer uncertain", "User and likely buyer identifiable", "Clear user, payer and procurement path"]),
    "digital_deployability": ("Digital deployability", ["Not meaningfully deployable as a digital product", "Major non-digital dependencies", "Digital component feasible with integration work", "Strong software/data delivery path", "Highly deployable, modular digital workflow"]),
    "scale_potential": ("Scale potential", ["One-off local use", "Narrow niche", "Replicable within one sector", "Multi-site / multi-sector replication plausible", "Platform/API-scale replication with low marginal delivery cost"]),
    "social_impact": ("Social/institutional impact", ["No clear impact pathway", "Limited local benefit", "Meaningful stakeholder benefit", "Strong institutional/social benefit", "Potentially large, measurable societal or public-value benefit"]),
}


@dataclass(frozen=True)
class QuestionRecord:
    question_id: str
    question: str
    time: float
    conceptual: float
    search: float
    experiment: float
    compute: float
    coordination: float
    l_before: float
    l_after: float
    market_pain: float = 2.0
    buyer_clarity: float = 2.0
    digital_deployability: float = 2.0
    scale_potential: float = 2.0
    social_impact: float = 2.0
    domain: str = "General"
    keyword: str = ""
    origin: str = "Human"
    scoring_mode: str = "Manual"
    confidence: str = "Not assessed"
    rationale: str = ""
    representation_before: str = ""
    representation_after: str = ""
    # DPT convention fields. None means use the declared worked-case/default scale.
    dc_scale: float | None = None
    qc_scale: float | None = None
    # Optional finite declared procedure set. Each item is a dict with the six DC components.
    # If None, the six top-level DC components define one admissible procedure.
    admissible_procedures: Any = None
    feasible: bool = True

    def to_dict(self):
        return asdict(self)


def clamp(x, lo, hi):
    return max(lo, min(hi, float(x)))


def _weights(weights: Sequence[float] | None = None) -> list[float]:
    w = [1.0] * 6 if weights is None else [float(x) for x in weights]
    if len(w) != 6 or any((not math.isfinite(x)) or x <= 0 for x in w):
        raise ValueError("DC weights must contain six finite positive values.")
    return w


def _procedure_vectors(record: QuestionRecord) -> list[tuple[str, list[float]]]:
    """Return the finite declared admissible procedure set used operationally.

    The theoretical DPT quantity is an infimum over admissible procedures. For a finite
    declared set, the infimum is the minimum. If no alternative set is supplied, the
    six top-level components are treated as one declared admissible procedure.
    """
    if not bool(record.feasible):
        return []

    raw = record.admissible_procedures
    if raw is None:
        vals = [clamp(getattr(record, k), 0, 4) for k in DC_COMPONENTS]
        return [("P1", vals)]

    if not isinstance(raw, (list, tuple)):
        raise ValueError("admissible_procedures must be a list/tuple of procedure records or None.")
    if len(raw) == 0:
        return []

    out: list[tuple[str, list[float]]] = []
    for i, proc in enumerate(raw, 1):
        if not isinstance(proc, dict):
            raise ValueError("Each admissible procedure must be a dictionary containing the six DC components.")
        vals = []
        for key in DC_COMPONENTS:
            if key not in proc:
                raise ValueError(f"Procedure {i} is missing DC component: {key}")
            vals.append(clamp(proc[key], 0, 4))
        out.append((str(proc.get("name", f"P{i}")), vals))
    return out


def procedure_costs(record: QuestionRecord, weights: Sequence[float] | None = None) -> list[dict]:
    """Scalarise each declared procedure cost vector C_omega = omega^T C."""
    w = _weights(weights)
    rows = []
    for name, vals in _procedure_vectors(record):
        raw_cost = sum(v * wi for v, wi in zip(vals, w))
        rows.append({"name": name, "components": dict(zip(DC_COMPONENTS, vals)), "raw_cost": raw_cost})
    return rows


def discovery_complexity(record: QuestionRecord, weights: Sequence[float] | None = None) -> float:
    """Operational raw DC: infimum over the finite declared admissible procedure set.

    For a nonempty finite set this equals the minimum scalarised procedure cost.
    If no admissible procedure is declared, DPT assigns +infinity.
    """
    costs = procedure_costs(record, weights)
    return min((p["raw_cost"] for p in costs), default=math.inf)


def dc_normalization_scale(record: QuestionRecord, weights: Sequence[float] | None = None) -> float:
    w = _weights(weights)
    scale = float(record.dc_scale) if record.dc_scale is not None else 4.0 * sum(w)
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("DC normalization scale a_D must be finite and > 0.")
    return scale


def normalized_discovery_complexity(record: QuestionRecord, weights: Sequence[float] | None = None) -> float:
    dc_raw = discovery_complexity(record, weights)
    if math.isinf(dc_raw):
        return math.inf
    return dc_raw / dc_normalization_scale(record, weights)


def selected_procedure(record: QuestionRecord, weights: Sequence[float] | None = None) -> str | None:
    costs = procedure_costs(record, weights)
    if not costs:
        return None
    return min(costs, key=lambda x: x["raw_cost"])["name"]


def signed_change(record: QuestionRecord) -> float:
    if float(record.l_before) <= 0 or float(record.l_after) < 0:
        raise ValueError("Description lengths require L(R)>0 and L(Rq)>=0.")
    return float(record.l_before) - float(record.l_after)


def compression_explanatory(record: QuestionRecord) -> bool:
    return signed_change(record) >= 0


def question_compression(record: QuestionRecord) -> float | None:
    """Formal raw QC = L(R)-L(Rq) for compression-explanatory questions."""
    delta = signed_change(record)
    return delta if delta >= 0 else None


def qc_normalization_scale(record: QuestionRecord) -> float:
    scale = float(record.qc_scale) if record.qc_scale is not None else float(record.l_before)
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("QC normalization scale a_Q must be finite and > 0.")
    return scale


def normalized_question_compression(record: QuestionRecord) -> float | None:
    qc_raw = question_compression(record)
    if qc_raw is None:
        return None
    return qc_raw / qc_normalization_scale(record)


def discovery_plane_eligible(record: QuestionRecord, weights: Sequence[float] | None = None) -> bool:
    dc_raw = discovery_complexity(record, weights)
    return bool(record.feasible) and math.isfinite(dc_raw) and compression_explanatory(record)


def classify_region(dc, qc, tau_d=.65, tau_q=.65):
    if dc is None or qc is None or not math.isfinite(float(dc)) or not math.isfinite(float(qc)):
        return "Excluded"
    if dc < tau_d and qc < tau_q:
        return "I"
    if dc < tau_d and qc >= tau_q:
        return "II"
    if dc >= tau_d and qc < tau_q:
        return "III"
    return "IV"


def region_interpretation(r):
    return {
        "I": "Routine / locally reorganising",
        "II": "Efficient high-compression",
        "III": "Costly / weakly compressive",
        "IV": "Costly / strongly reorganising",
        "Excluded": "Not assigned to the nonnegative Discovery Plane under the declared conventions",
    }[r]


def utility(dc, qc, lam=.5):
    if dc is None or qc is None or not math.isfinite(float(dc)) or not math.isfinite(float(qc)):
        return math.nan
    return float(qc) - float(lam) * float(dc)


def weighted_distance(a, b, w_d=1, w_q=1):
    if any(v is None for v in (*a, *b)):
        return math.nan
    return math.sqrt(w_d * (a[0] - b[0]) ** 2 + w_q * (a[1] - b[1]) ** 2)


def frontier_indices(points: Iterable[tuple[float, float]]) -> list[int]:
    pts = list(points)
    keep = []
    for i, (di, ci) in enumerate(pts):
        dominated = any(
            j != i and dj <= di and cj >= ci and (dj < di or cj > ci)
            for j, (dj, cj) in enumerate(pts)
        )
        if not dominated:
            keep.append(i)
    return keep


def coordinate_classes(points, tol=1e-9):
    classes = []
    for i, (d, c) in enumerate(points):
        found = False
        for cls in classes:
            rd, rc = cls["coordinate"]
            if abs(d - rd) <= tol and abs(c - rc) <= tol:
                cls["indices"].append(i)
                found = True
                break
        if not found:
            classes.append({"coordinate": (d, c), "indices": [i]})
    return classes


def venture_readiness(record, dc=None, qc=None, weights=None):
    # The venture heuristic uses normalized DPT coordinates and is therefore not
    # computed for questions excluded from the nonnegative Discovery Plane.
    if dc is None:
        dc = normalized_discovery_complexity(record)
    if qc is None:
        qc = normalized_question_compression(record)
    if qc is None or not math.isfinite(float(dc)):
        return math.nan

    p = [clamp(getattr(record, k), 0, 4) / 4 for k in VENTURE_POSITIVE]
    default = [.30, .20, .15, .10, .10, .10, .05]
    w = default if weights is None else list(map(float, weights))
    if len(w) != 7 or any(x < 0 for x in w) or sum(w) <= 0:
        raise ValueError("Venture weights require seven nonnegative values with positive total weight.")
    w = [x / sum(w) for x in w]
    features = [float(qc), 1 - float(dc), *p]
    return clamp(100 * sum(a * b for a, b in zip(w, features)), 0, 100)


def recommendation(score, frontier, compression_ok, attainable=True):
    if not attainable:
        return "Retain the signed change and provenance, but do not assign a nonnegative Discovery-Plane coordinate under the current conventions."
    if not compression_ok:
        return "Reframe the representation: the question expands the declared description language."
    if score is not None and math.isfinite(float(score)) and score >= 75 and frontier:
        return "Priority candidate for expert commercialization due diligence - not a startup-success prediction."
    if score is not None and math.isfinite(float(score)) and score >= 60:
        return "Promising; gather customer, technical, IP, ethics and pilot evidence before commercialization."
    if score is not None and math.isfinite(float(score)) and score >= 45:
        return "Develop further before commercialization screening; strengthen problem or solution evidence."
    return "Low current priority under the declared assumptions; revise the question or gather stronger evidence."


def next_action(dc, qc, score, frontier, attainable=True):
    if not attainable:
        return "Review the declared representation or procedure feasibility; preserve the expansion/inaccessibility record instead of forcing it onto the Discovery Plane."
    if qc >= .65 and dc >= .65:
        return "Reduce burden with a smaller proof-of-concept, pilot dataset, or narrower validation scope."
    if qc < .35 and dc < .65:
        return "Reframe or broaden the question before investing in commercialization work."
    if score >= 65 and frontier:
        return "Run structured customer/problem interviews and a technical proof-of-concept with stop/go criteria."
    if score < 50:
        return "Collect stronger problem, buyer and technical evidence before startup design."
    return "Validate the highest-uncertainty assumption first and record the result in the evidence log."


def readiness_stage(record, score):
    score_finite = score is not None and math.isfinite(float(score))
    return {
        "Research opportunity": "Strong" if score_finite and score >= 65 else "Developing / not established",
        "Technical feasibility": "Needs validation" if record.digital_deployability < 4 else "Plausible - validate",
        "Problem evidence": "Strong hypothesis" if record.market_pain >= 3 else "Weak / collect evidence",
        "Customer evidence": "Not collected unless documented",
        "Prototype": "Not built unless documented",
        "Pilot": "Not conducted unless documented",
        "IP": "Not assessed",
        "Regulatory": "Not assessed",
        "Business model": "Hypothesis",
        "Investment readiness": "Premature until external evidence is collected",
    }
