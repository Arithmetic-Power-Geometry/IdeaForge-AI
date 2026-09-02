from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ideaforge import QuestionRecord, analyse_records, sensitivity_grid


DATA = ROOT / "data"
RESULTS = ROOT / "results" / "six_question_demo"
FIGURES = ROOT / "figures" / "six_question_demo"

RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 1. Load the exact six demonstration cases used in paper
# ---------------------------------------------------------

required_ids = ["q1", "q2", "q3", "q4", "EDU1", "AGR1"]

raw = pd.read_csv(DATA / "session_test_cases.csv")

demo = raw[
    raw["question_id"].astype(str).isin(required_ids)
].copy()

found = set(demo["question_id"].astype(str))
missing = [qid for qid in required_ids if qid not in found]

if missing:
    raise ValueError(
        "Missing required demonstration cases: "
        + ", ".join(missing)
    )

# Preserve paper order
demo["question_id"] = pd.Categorical(
    demo["question_id"].astype(str),
    categories=required_ids,
    ordered=True,
)

demo = (
    demo.sort_values("question_id")
    .reset_index(drop=True)
)

fields = QuestionRecord.__dataclass_fields__

records = []

for _, row in demo.iterrows():
    payload = {
        name: row[name]
        for name in fields
        if name in demo.columns and not pd.isna(row[name])
    }

    if "confidence" not in payload:
        payload["confidence"] = (
            "Expert-declared"
            if payload.get("scoring_mode") == "Manual"
            else "Moderate"
        )

    records.append(
        QuestionRecord(**payload)
    )


# ---------------------------------------------------------
# 2. Analyse exact six-question demonstration portfolio
# ---------------------------------------------------------

results = analyse_records(
    records,
    tau_d=0.65,
    tau_q=0.65,
    lam=0.50,
)

results.to_csv(
    RESULTS / "six_question_portfolio.csv",
    index=False,
)


# ---------------------------------------------------------
# 3. Verify key q3 result reported in manuscript
# ---------------------------------------------------------

q3 = results.loc[
    results["question_id"].astype(str) == "q3"
].iloc[0]

checks = {
    "DC": abs(float(q3["dc"]) - 0.750) < 1e-9,
    "QC": abs(float(q3["qc"]) - 0.800) < 1e-9,
    "Region": str(q3["region"]) == "IV",
    "Frontier": bool(q3["frontier"]),
    "Utility": abs(float(q3["utility"]) - 0.425) < 1e-9,
    "Venture": abs(
        float(q3["venture_readiness"]) - 79.0
    ) < 1e-8,
}

if not all(checks.values()):
    raise AssertionError(
        f"q3 reproduction failed: {checks}"
    )


# ---------------------------------------------------------
# 4. Reproduce 196-setting sensitivity analysis
# ---------------------------------------------------------

grid = sensitivity_grid(records)

grid.to_csv(
    RESULTS / "six_question_sensitivity_grid.csv",
    index=False,
)

if len(grid) != 196:
    raise AssertionError(
        f"Expected 196 sensitivity configurations, "
        f"found {len(grid)}"
    )

ranking = (
    grid["top_question"]
    .value_counts(normalize=True)
    .mul(100)
    .rename("percent_top")
    .rename_axis("question_id")
    .reset_index()
)

ranking.to_csv(
    RESULTS / "six_question_ranking_stability.csv",
    index=False,
)

q3_percent = ranking.loc[
    ranking["question_id"].astype(str) == "q3",
    "percent_top",
]

if q3_percent.empty:
    raise AssertionError(
        "q3 was never top-ranked."
    )

q3_percent = float(q3_percent.iloc[0])


# ---------------------------------------------------------
# 5. Figure: six-question Discovery Plane
# ---------------------------------------------------------

eligible = results[
    results["discovery_plane_eligible"]
].copy()

fig, ax = plt.subplots(
    figsize=(7.6, 5.2)
)

ax.axvline(
    0.65,
    linestyle="--",
    linewidth=1,
)

ax.axhline(
    0.65,
    linestyle="--",
    linewidth=1,
)

for _, row in eligible.iterrows():
    ax.scatter(
        row["dc"],
        row["qc"],
        s=85,
    )

    ax.annotate(
        str(row["question_id"]),
        (row["dc"], row["qc"]),
        xytext=(5, 5),
        textcoords="offset points",
    )

frontier = (
    eligible[
        eligible["frontier"]
    ]
    .drop_duplicates(["dc", "qc"])
    .sort_values("dc")
)

ax.plot(
    frontier["dc"],
    frontier["qc"],
    linewidth=1.5,
    label="Nondominated coordinate frontier",
)

ax.legend()

ax.set(
    xlim=(0, 1.03),
    ylim=(0, 1.03),
    xlabel="Normalised Discovery Complexity",
    ylabel="Normalised Question Compression",
    title="IdeaForge AI six-question demonstration portfolio",
)

fig.tight_layout()

fig.savefig(
    FIGURES / "six_question_discovery_plane.png",
    dpi=220,
)

fig.savefig(
    FIGURES / "six_question_discovery_plane.pdf",
)

plt.close(fig)


# ---------------------------------------------------------
# 6. Figure: venture screen
# ---------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(7.6, 4.5)
)

ax.bar(
    results["question_id"].astype(str),
    results["venture_readiness"],
)

ax.set_ylim(0, 100)

ax.set_ylabel(
    "Transparent venture-readiness score"
)

ax.set_xlabel(
    "Candidate question"
)

ax.set_title(
    "Six-question commercialization screen"
)

for i, value in enumerate(
    results["venture_readiness"]
):
    ax.text(
        i,
        value + 1,
        f"{value:.1f}",
        ha="center",
        fontsize=8,
    )

fig.tight_layout()

fig.savefig(
    FIGURES / "six_question_venture_screen.png",
    dpi=220,
)

fig.savefig(
    FIGURES / "six_question_venture_screen.pdf",
)

plt.close(fig)


# ---------------------------------------------------------
# 7. Figure: ranking stability
# ---------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(7.6, 4.2)
)

ax.bar(
    ranking["question_id"],
    ranking["percent_top"],
)

ax.set_ylim(0, 105)

ax.set_ylabel(
    "Top-ranked across sensitivity grid (%)"
)

ax.set_title(
    "Ranking stability across 196 sensitivity settings",
    pad=12,
)

for i, value in enumerate(
    ranking["percent_top"]
):
    if value >= 98:
        ax.text(
            i,
            value - 3,
            f"{value:.1f}%",
            ha="center",
            va="top",
            fontsize=8,
        )
    else:
        ax.text(
            i,
            value + 1,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

fig.tight_layout()

fig.savefig(
    FIGURES / "six_question_ranking_stability.png",
    dpi=220,
)

fig.savefig(
    FIGURES / "six_question_ranking_stability.pdf",
)

plt.close(fig)


# ---------------------------------------------------------
# 8. Console verification
# ---------------------------------------------------------

print(
    "Six-question demonstration reproduced successfully."
)

print(
    f"Questions: {len(results)}"
)

print(
    f"Sensitivity configurations: {len(grid)}"
)

print(
    f"q3 top-ranked: {q3_percent:.1f}%"
)

print(
    "q3:",
    {
        "dc": float(q3["dc"]),
        "qc": float(q3["qc"]),
        "region": str(q3["region"]),
        "frontier": bool(q3["frontier"]),
        "utility": float(q3["utility"]),
        "venture_readiness":
            float(q3["venture_readiness"]),
    },
)
