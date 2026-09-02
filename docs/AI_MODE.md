# AI-Assisted Automatic Mode

AI-assisted automatic mode is a batch workflow rather than a one-question handoff.

1. Enter the number of questions to generate.
2. Enter topic/keyword/problem and domain.
3. Optionally provide background knowledge, available resources, and market/user context.
4. Generate the entire question set.
5. Review/edit/exclude questions.
6. Automatically produce a preliminary assessment for every retained question.
7. Review/edit all proposed scores and representation values.
8. Explicitly accept the batch before portfolio analysis.

The bundled transparent estimator uses declared text/context heuristics and is intended only to propose starting values. When an OpenAI key is configured, the optional LLM provider may supply the same structured fields. In either case, the application stores the mode, confidence, rationale, and final reviewed values.

No automatic estimate is an objective measurement of theoretical DPT quantities.
