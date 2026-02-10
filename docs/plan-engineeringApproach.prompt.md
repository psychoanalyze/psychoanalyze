**Technical Engineering Approach (Derived From docs/plan.d2)**

This project treats “how we build” as a chain of declarative artifacts that progressively constrain implementation: a requirements graph → a data contract → executable behavior specs (BDD) → a test hierarchy → atomic JJ TDD cycles. The intent is that every implementation step is justified by an upstream artifact and verified by CI.

**1) Start With A Declarative Requirements Graph**
- Use [plan.d2](plan.d2) as the top-level “map”: it defines the dependency order from requirements → tests → revision plan.
- Convert each “Target plot” node into an externally observable behavior set (inputs, outputs, invariants), then treat those behaviors as the driver for data and API shape.
- Keep this graph as the coordination surface: when scope changes, update the graph first, then let tests and implementation follow.

**2) Decompose “Target Plots” Into Data Interfaces (Not UI Work)**
- For each plot node (psychometric, threshold-vs-time, Weber, strength-duration, Bayes), work backwards into the minimal data it must consume.
- Treat the “Data Model” as an interface contract between layers:
  - Core tables (Trials → Points → Blocks → Sessions) define the upward-only aggregation pipeline.
  - Derived views (“Intensity”, “Time”, “Pulse Width”, etc.) define normalized projections for plotting/analysis (i.e., you build views, not ad-hoc plot-specific munging).
- Keep UI (Marimo) downstream: the notebook should orchestrate and visualize, not become the source of data transformations.

**3) Use The Data Contract As The Primary Cross-Stack Boundary**
- Keep the ODCS YAML contract as the canonical schema-level declaration, and validate it early and often.
- Make contract validation a “gate” that blocks plot work until the pipeline is producing compliant tables/views.
- Current tooling indicates contract checks are at least enforced via prek’s `datacontract lint` hook in [../prek.toml](../prek.toml). Treat that as the minimum bar; expand to runtime contract tests only when it buys meaningful safety.

**4) Translate Requirements Into Executable Acceptance Criteria (BDD)**
- Use the BDD scenarios in the plan as acceptance-level behavior statements (pipeline steps, plot generation, Gelman workflow).
- Keep BDD tests focused on “interfaces and invariants”:
  - Inputs/outputs exist and are shaped correctly.
  - Key invariants hold (e.g., rates are bounded, joins don’t duplicate rows, identifiers stable).
  - Workflow steps produce traceable artifacts (e.g., posterior summaries and diagnostics exist).
- Use the BDD layer to prevent “UI-driven” development: you can change implementation freely so long as behavior stays constant.

**5) Maintain A Test Hierarchy That Mirrors The Data Hierarchy**
- Implement tests in the same dependency direction as the data pipeline:
  - Trials aggregation tests (Trials → Points) come first.
  - Then fitting tests (Points → Blocks).
  - Then joins/views (Blocks ↔ Sessions, scaling views).
  - Then modeling layers (Weber, S-D, Bayesian).
- Enforce that each level’s tests only depend on stable outputs from the level below (no test should reach “down” into raw internals once a boundary is established).

**6) Execute Work As Atomic TDD Cycles (JJ-Style)**
- Treat each node in the “JJ Revisions” section as one Red → Green → Refactor unit:
  - Red: one failing test expressing one behavior at one boundary.
  - Green: minimal code to satisfy that test (avoid adding “future” helpers).
  - Refactor: only after green; extract helpers, improve naming/types, remove duplication.
- When a node becomes too broad, split it by boundary:
  - Example split axis: schema correctness vs numeric correctness vs join correctness vs plotting correctness.
  - Prefer splitting by interface contract rather than by file/module.

**7) Prefer Declarative Interfaces Between Components**
- Tables/views are interfaces between data modules.
- Schemas are interfaces between producers and consumers (contract + Pandera, where used).
- Plot functions are interfaces returning deterministic figures from immutable inputs (avoid embedding hidden state).
- The Marimo notebook is an orchestration interface: it composes library functions and renders outputs, but should not “own” transformation logic.

**8) CI-First Feedback Loops (Tight, Then Comprehensive)**
- Optimize for fast local feedback, then CI confidence:
  - Use the test watcher task (runs `uv run ptw . --now`) to stay in tight TDD loops.
  - Produce readable artifacts for regressions: Allure is already set up for serving reports and pytest config writes to `allure-results/`.
- Structure the pipeline so CI can run in layers:
  - Lint/format/typecheck gates first.
  - Contract lint/schema checks next.
  - Deterministic unit tests next (data transforms, fits with fixed seeds).
  - Heavier Bayesian sampling tests last (or nightly), using “smoke” checks in PR CI.

**9) Integrate Or Split Work Across The Stack (On Purpose)**
- Integrate vertically when you need a new boundary to exist:
  - Add contract shape → add minimal transform → add contract validation → add a minimal plot consuming it.
  - This creates an end-to-end slice without letting any layer get too far ahead.
- Split horizontally when a boundary is stable but breadth is expanding:
  - Once Trials → Points is stable, you can independently build: scaling views, joins, and multiple plot renderers.
- Keep “plot controls (scale/units)” late: treat them as a pure presentation layer that consumes already-normalized views (no data logic inside toggles).

**10) Documentation As A Build Artifact (Not A Side Task)**
- Keep [plan.d2](plan.d2) as the system map and keep it updated as you split/reorder work.
- When implementation changes boundaries, update documentation immediately (especially if it affects schemas, workflow steps, or test topology).
- Some docs and MkDocs nav entries may be out of sync with the current tree; treat doc drift as a CI smell and correct it as part of boundary changes.
