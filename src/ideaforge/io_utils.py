from __future__ import annotations
from pathlib import Path
import math
import pandas as pd
from .core import QuestionRecord


def _plain(value):
    """Convert pandas/numpy scalar values to plain Python values."""
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def load_worked_energy_case(csv_path: str | Path) -> list[dict]:
    """Load and validate the four-question worked energy case.

    The loader intentionally returns only fields accepted by QuestionRecord and
    supplies stable provenance metadata. It raises a clear ValueError if the
    source file is malformed, rather than allowing a later Streamlit failure.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Worked energy case not found: {path}")

    df = pd.read_csv(path)
    required = {
        "question_id", "question", "time", "conceptual", "search", "experiment",
        "compute", "coordination", "l_before", "l_after", "market_pain",
        "buyer_clarity", "digital_deployability", "scale_potential", "social_impact",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Worked energy case is missing columns: {', '.join(missing)}")
    if len(df) != 4:
        raise ValueError(f"Worked energy case must contain exactly 4 questions; found {len(df)}.")

    records: list[dict] = []
    allowed = set(QuestionRecord.__dataclass_fields__)
    for raw in df.to_dict("records"):
        payload = {k: _plain(v) for k, v in raw.items() if k in allowed}
        payload.update(
            domain="Engineering",
            keyword="university campus energy",
            origin="Worked energy case",
            scoring_mode="Manual",
            confidence="Source-worked",
            rationale="Values reproduce the declared worked university-energy case.",
        )
        # Validate arithmetic constraints now so UI loading cannot silently fail later.
        record = QuestionRecord(**payload)
        numeric_04 = [
            record.time, record.conceptual, record.search, record.experiment,
            record.compute, record.coordination, record.market_pain,
            record.buyer_clarity, record.digital_deployability,
            record.scale_potential, record.social_impact,
        ]
        if any((not math.isfinite(float(v))) or float(v) < 0 or float(v) > 4 for v in numeric_04):
            raise ValueError(f"Worked energy case contains an out-of-range 0-4 score for {record.question_id}.")
        if float(record.l_before) <= 0 or float(record.l_after) < 0:
            raise ValueError(f"Invalid description lengths for {record.question_id}.")
        records.append(record.to_dict())
    return records
