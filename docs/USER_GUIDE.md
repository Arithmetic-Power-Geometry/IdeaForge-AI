# IdeaForge AI v1.0.0 - Professional User Guide

## 1. Select the mode

The first control in the main application is a radio selector:

- **AI-assisted automatic** - generates a complete question set and proposes preliminary scores for every selected question.
- **Manual expert** - the user declares every question, every score, and the representation values directly.

Changing the mode starts a clean workflow in that mode.

## 2. Six-stage workflow

### Stage 1 - Setup

**AI-assisted automatic:** enter the number of questions first, then the topic/keyword/problem, domain, generation goal, novelty orientation, and optional background/resource/market context.

**Manual expert:** enter the number of questions, domain, and optional topic/project label.

### Stage 2 - Questions

The full question set is visible before scoring.

- AI mode shows all generated questions in one editable table. Every question is selected by default and may be edited or excluded.
- Manual mode shows one editable question table with IDs and question text.

### Stage 3 - Scoring

**AI-assisted automatic:** every retained question receives a preliminary estimate for the six DC components, `L(R)`, `L(Rq)`, the five commercialization dimensions, confidence, and rationale. All values remain editable. The batch is stored only after explicit acceptance.

**Manual expert:** every question has a complete score form. Each 0-4 input has a help popover. The representation fields have a separate help popover. Live DC and QC calculations appear before submission.

### Stage 4 - Portfolio

The application reports:

- Discovery Complexity (DC)
- Question Compression (QC)
- signed representational change
- Region I-IV
- frontier membership
- coordinate-equivalence class
- regularized utility
- venture-readiness heuristic
- recommendation and next action

The Discovery Plane plot and a 196-configuration sensitivity audit are available here.

### Stage 5 - Startup Studio

Select any portfolio question and document:

- problem/pain
- proposed solution
- target users
- paying customer
- value proposition
- alternatives
- differentiation
- required data
- core technology
- MVP
- pilot KPIs
- revenue options
- cost drivers
- partners
- IP/privacy/security/regulatory/ethical risks

The readiness table explicitly distinguishes a strong screen from customer evidence, prototype evidence, pilot evidence, IP/regulatory status, and investment readiness.

### Stage 6 - Export evidence

Download:

- complete portfolio CSV
- complete portfolio JSON
- per-question assessment PDF

Startup Studio entries remain visible for the selected question.

## 3. Discovery Complexity guidance (0-4)

### Time requirement
0 almost immediate; 1 short bounded effort; 2 moderate duration; 3 long/multi-stage; 4 unusually long or highly uncertain.

### Conceptual distance
0 direct application; 1 small extension; 2 moderate integration; 3 major cross-domain/theoretical integration; 4 foundational conceptual leap.

### Search/literature burden
0 readily identifiable evidence; 1 focused search; 2 broad manageable review; 3 fragmented multi-domain evidence; 4 very dispersed or difficult evidence.

### Experimental burden
0 no meaningful experiment; 1 simple validation; 2 moderate controlled study; 3 substantial field deployment/specialized resources; 4 very demanding or long-term experimentation.

### Computational burden
0 negligible; 1 routine standard hardware; 2 moderate modelling; 3 large-scale/specialized computation; 4 unusually intensive or frontier-scale computation.

### Coordination burden
0 individual work; 1 small team; 2 several roles/one unit; 3 multiple teams/stakeholders/sites; 4 extensive multi-institutional/regulatory coordination.

With equal weights, each admissible procedure has raw scalar cost equal to the sum of its six components. If more than one admissible procedure is declared, raw DC is the minimum of those costs (the infimum on the finite declared set). The default normalized DC divides raw DC by a_D=24.

## 4. Representation help

`L(R)` is the declared description length of the representation before the question reorganizes it. `L(Rq)` is the length after reorganization. Use one coding language consistently, such as proposition counts, graph-description units, ontology statements, or another auditable proxy.

`Delta L = L(R) - L(Rq)`

For a compression-explanatory question (`L(Rq) <= L(R)`):

`raw QC = Delta L`

`normalized QC = raw QC / a_Q`

The default worked-case convention uses `a_Q = L(R)`. If `L(Rq) > L(R)`, the signed change is negative. IdeaForge retains that expansion record and its provenance but does **not** assign it a nonnegative Discovery-Plane coordinate, region, frontier status, utility, or DPT-dependent venture score.

## 5. Commercialization guidance (0-4)

### Market/problem pain
0 no demonstrated problem → 4 critical, costly, or strategically urgent pain.

### Buyer/user clarity
0 no identifiable user/buyer → 4 clear user, payer, and procurement path.

### Digital deployability
0 not meaningfully digital → 4 highly deployable modular digital workflow.

### Scale potential
0 one-off local use → 4 platform/API-scale replication with low marginal delivery cost.

### Social/institutional impact
0 no clear impact pathway → 4 potentially large measurable societal/public-value benefit.

These are separate commercialization judgments, not DPT constructs.

## 6. Default settings

- DC threshold: 0.65
- QC threshold: 0.65
- Utility cost penalty lambda: 0.50
- DC component weights: equal
- Venture weights: QC 0.30, inverse DC 0.20, market pain 0.15, buyer clarity 0.10, digital deployability 0.10, scale 0.10, social impact 0.05

Thresholds are analytical conventions, not natural laws.

## 7. Worked energy case

The public demo loader contains only q1-q4. q3 reproduces DC 0.750, QC 0.800, Region IV, frontier membership, U0.5 0.425, and venture screen 79.0 under the default settings.

## 8. Responsible use

IdeaForge is an auditable early-stage decision-support tool. It does not replace domain expertise, research ethics, peer review, technology-transfer offices, customer discovery, IP/FTO review, safety/security assessment, regulatory review, pilot validation, or investment diligence.
