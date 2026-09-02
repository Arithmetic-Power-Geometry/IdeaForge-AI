from __future__ import annotations

import math
import pandas as pd
from .core import *


def analyse_records(records, tau_d=.65, tau_q=.65, lam=.5, dc_weights=None, venture_weights=None, equiv_tol=1e-9):
    rows = []
    eligible_points: list[tuple[float, float]] = []
    eligible_row_indices: list[int] = []

    for r in records:
        dc_raw = discovery_complexity(r, dc_weights)
        dc = normalized_discovery_complexity(r, dc_weights)
        delta = signed_change(r)
        qc_raw = question_compression(r)
        qc = normalized_question_compression(r)
        eligible = discovery_plane_eligible(r, dc_weights)
        region = classify_region(dc if eligible else None, qc if eligible else None, tau_d, tau_q)
        vr = venture_readiness(r, dc if eligible else None, qc if eligible else None, venture_weights) if eligible else math.nan

        row = {
            **r.to_dict(),
            "dc_raw": dc_raw,
            "dc_scale_used": dc_normalization_scale(r, dc_weights),
            "dc": dc,
            "selected_procedure": selected_procedure(r, dc_weights),
            "procedure_count": len(procedure_costs(r, dc_weights)),
            "delta_l": delta,
            "qc_raw": qc_raw if qc_raw is not None else math.nan,
            "qc_scale_used": qc_normalization_scale(r),
            "qc": qc if qc is not None else math.nan,
            "compression_explanatory": compression_explanatory(r),
            "discovery_plane_eligible": eligible,
            "region": region,
            "region_meaning": region_interpretation(region),
            "utility": utility(dc if eligible else None, qc if eligible else None, lam),
            "venture_readiness": vr,
        }
        rows.append(row)
        if eligible:
            eligible_row_indices.append(len(rows) - 1)
            eligible_points.append((float(dc), float(qc)))

    frontier_local = set(frontier_indices(eligible_points)) if eligible_points else set()
    classes = coordinate_classes(eligible_points, equiv_tol) if eligible_points else []
    class_map_local = {}
    for ci, cls in enumerate(classes, 1):
        for local_idx in cls["indices"]:
            class_map_local[local_idx] = ci

    eligible_lookup = {row_idx: local_idx for local_idx, row_idx in enumerate(eligible_row_indices)}
    for i, row in enumerate(rows):
        if i in eligible_lookup:
            local_idx = eligible_lookup[i]
            row["frontier"] = local_idx in frontier_local
            row["coordinate_class"] = class_map_local[local_idx]
        else:
            row["frontier"] = False
            row["coordinate_class"] = None

        row["recommendation"] = recommendation(
            row["venture_readiness"], row["frontier"], row["compression_explanatory"], row["discovery_plane_eligible"]
        )
        row["next_action"] = next_action(
            row["dc"] if row["discovery_plane_eligible"] else math.nan,
            row["qc"] if row["discovery_plane_eligible"] else math.nan,
            row["venture_readiness"],
            row["frontier"],
            row["discovery_plane_eligible"],
        )

    return pd.DataFrame(rows)


def sensitivity_grid(records, thresholds=(.55, .60, .65, .70, .75, .80, .85), lambdas=(.25, .5, .75, 1.0)):
    out = []
    for td in thresholds:
        for tq in thresholds:
            for lam in lambdas:
                df = analyse_records(records, td, tq, lam)
                eligible = df[df.discovery_plane_eligible].copy()
                if len(eligible):
                    rank = eligible.sort_values(["frontier", "venture_readiness", "utility"], ascending=[False, False, False]).iloc[0]
                    out.append({
                        "tau_d": td,
                        "tau_q": tq,
                        "lambda": lam,
                        "top_question": rank.question_id,
                        "top_utility": rank.utility,
                        "top_venture": rank.venture_readiness,
                    })
    return pd.DataFrame(out)
