from pathlib import Path
import sys, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import pandas as pd
import matplotlib.pyplot as plt
from ideaforge import *

RESULTS = ROOT / 'results'
FIG = ROOT / 'figures'
RESULTS.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

raw = pd.read_csv(ROOT / 'data' / 'session_test_cases.csv')
fields = QuestionRecord.__dataclass_fields__

recs = []
for _, r in raw.iterrows():
    d = {
        k: r[k]
        for k in fields
        if k in raw.columns and not pd.isna(r[k])
    }

    if 'confidence' not in d:
        d['confidence'] = (
            'Expert-declared'
            if d.get('scoring_mode') == 'Manual'
            else 'Moderate'
        )

    recs.append(QuestionRecord(**d))

df = analyse_records(recs)
df.to_csv(
    RESULTS / 'all_tested_questions_analysis.csv',
    index=False
)

energy = df[
    df.question_id.isin(['q1', 'q2', 'q3', 'q4'])
].copy()

energy.to_csv(
    RESULTS / 'worked_energy_analysis.csv',
    index=False
)

sg = sensitivity_grid(recs)
sg.to_csv(
    RESULTS / 'sensitivity_grid.csv',
    index=False
)

freq = (
    sg.top_question
    .value_counts(normalize=True)
    .mul(100)
    .rename('percent_top')
    .rename_axis('question_id')
    .reset_index()
)

freq.to_csv(
    RESULTS / 'ranking_stability.csv',
    index=False
)

# ---------------------------------------------------------
# Threshold sensitivity for q3
# ---------------------------------------------------------

rows = []

for t in [.60, .65, .75, .80, .85]:
    r = analyse_records(
        [recs[2]],
        t,
        t,
        .5
    ).iloc[0]

    rows.append({
        'threshold': t,
        'region': r.region
    })

pd.DataFrame(rows).to_csv(
    RESULTS / 'q3_threshold_sensitivity.csv',
    index=False
)


# ---------------------------------------------------------
# Figure 1: System architecture
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 2.4))
ax.axis('off')

labels = [
    'Keyword /\nproblem',
    'Question\ngenerator',
    'Manual or AI-\nassisted review',
    'DPT:\nDC + QC',
    'Frontier +\nsensitivity',
    'Startup\nStudio',
    'MVP + pilot +\nevidence'
]

for i, label in enumerate(labels):
    x = .07 + i * .145

    ax.text(
        x,
        .5,
        label,
        ha='center',
        va='center',
        bbox=dict(
            boxstyle='round,pad=.55',
            fc='white',
            ec='0.45'
        )
    )

    if i < len(labels) - 1:
        ax.annotate(
            '',
            xy=(x + .09, .5),
            xytext=(x + .055, .5),
            arrowprops=dict(
                arrowstyle='->',
                lw=1.5
            )
        )

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

fig.tight_layout()

fig.savefig(
    FIG / 'fig_system_pipeline.png',
    dpi=220,
    bbox_inches='tight'
)

fig.savefig(
    FIG / 'fig_system_pipeline.pdf',
    bbox_inches='tight'
)

plt.close(fig)


# ---------------------------------------------------------
# Figure 2: Discovery Plane — all test cases
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(7.6, 5.2))

ax.axvline(
    .65,
    ls='--',
    lw=1
)

ax.axhline(
    .65,
    ls='--',
    lw=1
)

for _, r in df.iterrows():
    ax.scatter(
        r.dc,
        r.qc,
        s=85
    )

    ax.annotate(
        r.question_id,
        (r.dc, r.qc),
        xytext=(5, 5),
        textcoords='offset points'
    )

fr = (
    df[df.frontier]
    .drop_duplicates(['dc', 'qc'])
    .sort_values('dc')
)

ax.plot(
    fr.dc,
    fr.qc,
    lw=1.5,
    label='Nondominated coordinate frontier'
)

ax.legend()

ax.set(
    xlim=(0, 1.03),
    ylim=(0, 1.03),
    xlabel='Normalised Discovery Complexity',
    ylabel='Normalised Question Compression',
    title='IdeaForge AI tested portfolio'
)

fig.tight_layout()

fig.savefig(
    FIG / 'fig_portfolio_plane.png',
    dpi=220
)

fig.savefig(
    FIG / 'fig_portfolio_plane.pdf'
)

plt.close(fig)


# ---------------------------------------------------------
# Figure 3: Venture screens
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(7.6, 4.5))

ax.bar(
    df.question_id,
    df.venture_readiness
)

ax.set_ylim(0, 100)

ax.set_ylabel(
    'Transparent venture-readiness score'
)

ax.set_xlabel(
    'Candidate question'
)

ax.set_title(
    'Separate commercialization screen'
)

for i, v in enumerate(df.venture_readiness):
    ax.text(
        i,
        v + 1,
        f'{v:.1f}',
        ha='center',
        fontsize=8
    )

fig.tight_layout()

fig.savefig(
    FIG / 'fig_venture_portfolio.png',
    dpi=220
)

fig.savefig(
    FIG / 'fig_venture_portfolio.pdf'
)

plt.close(fig)


# ---------------------------------------------------------
# Figure 4: Sensitivity stability
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(7.6, 4.2))

ax.bar(
    freq.question_id,
    freq.percent_top
)

# Small visual headroom prevents the 100% label
# from colliding with the figure title.
ax.set_ylim(0, 105)

ax.set_ylabel(
    'Top-ranked across sensitivity grid (%)'
)

ax.set_title(
    'Ranking stability across 196 threshold/lambda settings',
    pad=12
)

for i, v in enumerate(freq.percent_top):
    if v >= 98:
        # Put labels for bars at/near 100% inside the bar.
        ax.text(
            i,
            v - 3,
            f'{v:.1f}%',
            ha='center',
            va='top',
            fontsize=8
        )
    else:
        ax.text(
            i,
            v + 1,
            f'{v:.1f}%',
            ha='center',
            va='bottom',
            fontsize=8
        )

fig.tight_layout()

fig.savefig(
    FIG / 'fig_sensitivity.png',
    dpi=220
)

fig.savefig(
    FIG / 'fig_sensitivity.pdf'
)

plt.close(fig)


# ---------------------------------------------------------
# Console summary
# ---------------------------------------------------------

print(
    f'Reproduced {len(df)} test questions; '
    f'frontier={int(df.frontier.sum())}; '
    f'coordinate_classes={df.coordinate_class.nunique()}; '
    f'sensitivity_runs={len(sg)}'
)

print(
    'Energy q3:',
    energy[
        energy.question_id == 'q3'
    ][
        [
            'dc',
            'qc',
            'region',
            'frontier',
            'utility',
            'venture_readiness'
        ]
    ].to_dict('records')[0]
)
