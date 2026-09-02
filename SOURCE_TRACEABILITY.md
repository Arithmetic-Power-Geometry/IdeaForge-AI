# Source Traceability

## Source-derived foundations
- Discovery Plane Theory definitions and boundaries are based on the supplied DPT manuscript and worked guide. The implementation distinguishes formal raw DC/QC from normalized coordinates, computes the finite-set procedure infimum as a minimum, and excludes representational expansion or procedure infeasibility from the nonnegative Discovery Plane while retaining signed change and provenance.
- The worked university-energy q1-q4 inputs reproduce the supplied guide.
- DiscoveryBench v1.1.0 and the prior 20-field benchmark are retained only as reported summaries where raw records were not supplied.

## Development/test cases
- `EDU1` records the student-dropout question used during interface testing with explicitly illustrative manual values.
- `AGR1` is an explicitly illustrative AI-assisted demonstration case.
- No test question is presented as an empirical discovery, validated startup, or historical outcome.

## External literature
The manuscript bibliography uses identifiable journal, conference, book, arXiv, and Zenodo records. Recent references include 2024-2026 literature on AI-for-science, self-driving laboratories, auditable question formation, ResearchBench, entrepreneurial universities, and technology transfer.

## Software-generated evidence
`python scripts/reproduce.py` regenerates the six-question analysis, 196-setting sensitivity grid, ranking-stability report, q3 threshold sensitivity table, and four manuscript figures. These outputs are deterministic under the bundled inputs and defaults.

## Interface-test history
`data/interface_test_history.csv` preserves the earlier default-value tests (including duplicate 0.5/0.5 coordinates) as UI-development records. They are explicitly marked non-substantive and are not mixed into the six-question analytic demonstration.
