# Agent orchestration (iterative dev + CI/CD)

This guide is a **down-in-the-weeds, engineering-first** blueprint for building agentic systems that remain debuggable, testable, and shippable.

It focuses on:

- Iterative development loops (tight local feedback, safe refactors)
- CI/CD integration (lint/type/test/evals + release gates)
- Parallelization + orchestration (DAGs, queues, and artifact-driven dataflow)
- Context-window monitoring (token budgets, retrieval, and summarization)
- Practical boundaries between **agentic** vs **deterministic** code
- An implementation sketch using **`pydantic-ai`**, **DSPy**, **ADK**, and **atomic-agents**

## First principles

### 1) Determinism is the default

Prefer deterministic code for anything that can be expressed as:

- A pure transform (input → output)
- A contract (schema validation)
- A known algorithm (parsing, diffing, static analysis, metric calculation)
- A repeatable side effect (writing files, calling APIs with idempotency keys)

Agents should be reserved for tasks where the objective is under-specified or requires judgment:

- Planning, decomposition, and prioritization
- Synthesis from multiple sources
- Generating candidate code patches
- Explaining trade-offs and writing human-facing docs

### 2) Everything important becomes an artifact

Orchestration gets tractable when every step reads/writes typed artifacts.

- Artifacts are **immutable** (content-addressed) or versioned.
- Artifacts are **typed** (Pydantic models) and validated at boundaries.
- Artifacts are **traceable** (linked to inputs + prompt versions + model + tools).

This gives you:

- Repeatability
- Caching
- Parallel execution
- Auditable runs (and cheap re-runs)

### 3) Agents are I/O adapters over stable cores

The stable core is your deterministic library code (parsers, validators, evaluators, data pipeline). Agents sit at the edges:

- They decide *what to do next*, not *how your core algorithms work*.
- They output structured plans/instructions that deterministic executors implement.

## Architecture: dataflow-first orchestration

Model your system as a DAG of steps.

- Nodes: deterministic functions or agent calls
- Edges: typed artifacts
- Scheduler: executes ready nodes concurrently

### Canonical layers

1. **Domain core (deterministic)**
   - Pure functions + schemas + metrics
   - No LLM calls

2. **Boundary adapters (deterministic)**
   - Tool wrappers (filesystem, git/jj, HTTP)
   - Idempotency, retries, rate limiting

3. **Agent layer (probabilistic)**
   - Planning / routing / synthesis
   - Outputs typed results validated at boundaries

4. **Orchestration runtime (deterministic)**
   - DAG scheduler
   - Artifact store
   - Context-window budget tracking
   - Tracing + eval hooks

## Context-window monitoring (token budgets)

You need a *mechanical sympathy* plan for context windows. The failure mode is predictable: the system silently drops context and becomes inconsistent.

### Treat context like a budgeted resource

Maintain explicit budgets per run:

- `max_input_tokens`: model limit
- `reserved_tokens`: headroom for tool output + chain-of-thought (don’t rely on hidden reasoning) + structured JSON
- `retrieval_budget`: how many chunks/files you can afford
- `history_budget`: how much conversation state you keep verbatim

### Strategy

- **Prefer references over copies**: store raw docs/files as artifacts; feed only summaries or extracted spans.
- **Chunk + retrieve**: embeddings/lexical retrieval into relevant fragments.
- **Summarize into state**: maintain a compact “working set” artifact (facts, decisions, constraints).
- **Validate invariants**: if the plan depends on a file, ensure the artifact includes its hash.

### Practical implementation patterns

- A `ContextEnvelope` model that includes:
  - constraints
  - current goal
  - allowed tools
  - selected artifacts (IDs + hashes)
  - summary state
  - budget counters

- A `ContextAuditor` that runs before every agent call:
  - checks budget
  - prunes/re-summarizes
  - enforces “no raw giant file dumps”

## Parallelization + orchestration

### What can be parallelized safely

- Independent retrievals (read different files, docs)
- Static analysis steps (lint/type/test shards)
- Independent subtasks that write **disjoint artifacts**

### What should stay serialized

- Mutating the same file(s)
- Applying patches to the same module
- Rebases/merges
- Any action that depends on human review

### Orchestration primitives

- **Map-reduce** for research/synthesis
  - Map: multiple specialists summarize parts
  - Reduce: one agent composes final plan + conflicts

- **Speculative execution** for codegen
  - Run multiple candidate solutions; deterministic evaluator picks the best

- **Gated execution**
  - Agent proposes plan → deterministic validator checks → executor performs

## Iterative development loop (local)

A practical “agentic TDD” loop that stays disciplined:

1. Write/adjust one failing test (deterministic)
2. Ask agent to propose the minimal patch (probabilistic)
3. Apply patch, run tests (deterministic)
4. Refactor with guardrails (probabilistic suggestions, deterministic checks)

For this repo specifically, you already have:

- Ruff formatting + lint
- `ty` type checking
- Pytest (plus Allure)
- Pre-commit hooks via `prek.toml`

## CI/CD integration

### CI: required checks (typical)

At minimum, run these in CI on pull requests:

- `ruff` (format + lint)
- `ty` (type check)
- `pytest` (unit tests + BDD if desired)
- `marimo check` (if notebooks are a product surface)
- `datacontract lint` (data contract regression)
- Agent eval suite (offline, deterministic scoring)

### CD: release/deploy gates

You generally want:

- Tags/releases only after CI green
- Semantic versioning automation (you already have `tool.semantic_release` configured)
- Docs/dashboard deployment triggered on main (you already deploy `_site` via marimo export)

### A concrete workflow sketch

Add a CI workflow (example only; adjust to your org conventions):

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v7
      - run: uv sync --all-extras
      - run: uv run ruff format --check .
      - run: uv run ruff check .
      - run: uv run ty check
      - run: uv run pytest
```

For agent systems, add an **eval job** that runs a frozen dataset through your orchestrator and asserts quality thresholds.

## Evals: making “agent quality” testable

### Types of evals

- **Unit evals**: validate that structured outputs conform to schema and invariants
- **Golden evals**: run fixed prompts + fixed tools + check exact output (when feasible)
- **Metric evals**: judge via deterministic metrics (JSON validity, compile/test pass rate, edit distance)
- **Model-graded evals**: use another model as a judge, but lock prompt + judge model, and treat it as probabilistic

### A recommended setup

- Store eval cases as artifacts (YAML/JSONL)
- Each case defines:
  - inputs
  - allowed tools
  - expected schema
  - deterministic scoring function(s)

- Gate merges on:
  - schema pass rate
  - minimum score
  - no regressions vs baseline

DSPy is a good fit for *prompt/program optimization* against an eval set.

## Tooling boundaries: agentic vs deterministic

### Deterministic (should be code)

- Parsing, validation, and data transforms
- File edits and patch application mechanics
- Metric computation and scoring
- Test running, linting, type checking
- Artifact storage and versioning

### Agentic (should be agents)

- Choosing which step to run next
- Interpreting ambiguous requirements
- Writing human-readable docs
- Suggesting alternative implementations

### The boundary rule

If a step can be verified with a deterministic checker, it should:

- Accept typed inputs
- Produce typed outputs
- Be executed deterministically
- Have an eval/metric

Agents may propose, but deterministic systems dispose.

## Implementation sketch (pydantic-ai + DSPy + ADK + atomic-agents)

This is a conceptual sketch — treat it as a template.

### 1) Typed artifacts (Pydantic)

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class ArtifactRef(BaseModel):
    id: str
    sha256: str
    media_type: str


class PatchPlan(BaseModel):
    target_files: list[str]
    unified_diff: str
    rationale: str


class EvalResult(BaseModel):
    score: float
    passed: bool
    details: dict[str, str] = Field(default_factory=dict)
```

### 2) Deterministic core: validators + executors

```python
def validate_patch_plan(plan: PatchPlan) -> None:
    if not plan.target_files:
        raise ValueError("No target files")
    if "*** Begin Patch" not in plan.unified_diff:
        raise ValueError("Expected apply_patch-style diff")


def apply_patch_plan(plan: PatchPlan) -> ArtifactRef:
    # Implementation uses your editor/CI mechanics; keep this deterministic.
    ...
```

### 3) Agent adapters with `pydantic-ai`

Use `pydantic-ai` to ensure the agent returns structured outputs.

```python
from pydantic_ai import Agent

patch_agent = Agent(
    model="...",
    result_type=PatchPlan,
)

async def propose_patch(context: str) -> PatchPlan:
    return await patch_agent.run(context)
```

The key point: **schema validation is your first line of defense**.

### 4) DSPy for optimization + eval-driven development

DSPy’s sweet spot is turning “prompt engineering” into “program optimization” against a dataset.

- Define a DSPy program that maps context → structured result
- Define a metric (deterministic if possible)
- Run optimization to improve pass rate

```python
# Pseudocode: exact DSPy APIs depend on your chosen version
# program = dspy.ChainOfThought(...)
# tuned = dspy.teleprompt.BootstrapFewShot(metric=...)(program, trainset=...)
```

Use DSPy to **tune the plan/patch agents** while keeping the *executor* deterministic.

### 5) ADK for multi-agent graphs (planning + routing)

ADK (Agent Development Kit) is useful when you want a graph of specialized agents:

- Planner → assigns tasks to specialists
- Specialists → produce typed artifacts
- Reducer → reconciles + emits final plan

You still keep:

- A deterministic scheduler
- Typed artifacts
- Deterministic gates before side effects

### 6) atomic-agents for specialization boundaries

Use atomic agent patterns to keep roles small and composable:

- `RetrieverAgent`: “find relevant files/artifacts”
- `SummarizerAgent`: “compress into constraints/facts”
- `PlannerAgent`: “emit a DAG of steps”
- `PatchAgent`: “emit PatchPlan”
- `ReviewAgent`: “emit risks/edge cases”

Each “atomic” agent:

- Has one job
- Has typed I/O
- Is easy to eval independently

## A practical orchestration plan (end-to-end)

### Run loop

1. Ingest request → create `RunContext` artifact
2. Retrieve relevant artifacts (parallel)
3. Build/refresh `WorkingSetSummary` (budgeted)
4. Planner emits a `TaskDAG`
5. Scheduler executes DAG nodes:
   - deterministic nodes run directly
   - agent nodes run through `pydantic-ai` adapters
6. Every side effect step is gated:
   - schema validation
   - policy checks (allowed files/tools)
   - dry-run diff
7. Run evals on outputs and store results
8. Emit final report

### Context-window monitoring in the loop

- Before every agent call: `ContextAuditor`
- After every node: update `BudgetReport`
- If budgets exceeded: prune + summarize + re-run planner

## Suggested repo layout (optional)

If you decide to implement this in-repo, a clean separation looks like:

- `src/psychoanalyze/orchestrator/` (scheduler, artifacts, budgets, tracing)
- `src/psychoanalyze/agents/` (pydantic-ai / ADK / atomic agents adapters)
- `src/psychoanalyze/evals/` (datasets + scorers + runners)
- `tests/evals/` (CI gates for eval thresholds)

## Quick checklist

- Deterministic core functions have unit tests
- Agent outputs are schema-validated (Pydantic)
- Side effects are gated and idempotent
- Orchestration is DAG/dataflow with typed artifacts
- Context window is explicitly budgeted and audited
- CI runs: ruff + ty + pytest + contract lint + marimo check + evals
- DSPy tuning runs offline against an eval dataset
