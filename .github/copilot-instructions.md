# PsychoAnalyze - Copilot Instructions

## Project Overview

PsychoAnalyze is a Python library for interactive data simulation and analysis in psychophysics research. It models psychometric functions using logistic regression to estimate detection thresholds from experimental trial data.

## Architecture

PsychoAnalyze is organized around **three loosely-coupled pillars** (see `docs/architecture.md`):
1. **Data processing** (deterministic transforms + validation)
2. **Interactive dashboard** (Marimo UI that orchestrates and visualizes)
3. **Ergonomic Python package** (stable API/CLI for scripting + automation)

### Data Hierarchy (core concept)
The codebase follows a strict hierarchical data model where each level aggregates the one below:
1. **Trials** (raw table) - Individual stimulus presentations (e.g., `Intensity`, `Result`, `Block`)
2. **Points** (`src/psychoanalyze/data/points.py`) - Aggregated trial counts at each intensity (Hit Rate = Hits / n trials)
3. **Blocks** (`src/psychoanalyze/data/blocks.py`) - Fitted psychometric curves (threshold + slope from logistic regression)
4. **Sessions/Subjects** (`src/psychoanalyze/data/sessions.py`, `src/psychoanalyze/data/subjects.py`) - Longitudinal groupings

Each module in `src/psychoanalyze/data/` corresponds to one level. Functions typically transform data upward (e.g., `psychoanalyze.data.points.from_trials()` aggregates trials into points).

### Key Components
- **`app.py`** - Marimo app serving as the interactive dashboard UI (orchestration + visualization; keep transforms in `src/psychoanalyze/`)
- **`src/psychoanalyze/`** - Core library
  - `data/` - Data manipulation per hierarchy level
  - `analysis/` - Statistical analysis (Bayesian, ECDF, Weber, strength-duration)
  - `sigmoids.py` - Psychometric link functions (Weibull, Gumbel, Quick)
  - `plot.py` - Plotly template and axis settings
- **`models/`** - dbt SQL models and Stan models for Bayesian fitting

### The Psychometric Function (ψ)
Core formula used throughout: `ψ(x) = γ + (1 - γ - λ) * F(x; x₀, k)`
- `x₀` = threshold (50% point), `k` = slope (steepness)
- `γ` = guess rate, `λ` = lapse rate
- `F` = link function (typically logistic sigmoid)

## Development Workflow

**Shell:** Nushell is the default shell for this project. All commands should be written in Nushell syntax unless explicitly running bash/sh scripts.

**MCP-first:** Prefer MCP tools over shell commands when available (see `.github/instructions/prefer-mcp-tools.instructions.md`). Check for `mcp_jj_*`, `mcp_marimo_*`, `runTests`, and dependency management tools before falling back to `run_in_terminal`. Always call `configure_python_environment` before any Python-related tool.

```bash
# Package management (uv only, not pip)
uv sync                      # Install all dependencies from lock file
uv add <package>             # Add/install a new package to dependencies
uv add --dev <package>       # Add/install a new dev dependency
uv run ruff format           # Format
uv run ruff check --fix      # Lint and autofix
uv run ty check              # Type check (uses ty, not mypy)
uv run pytest                # Run tests (writes Allure results to allure-results/)
uv run ptw . --now           # Test watcher (tight TDD loop)

# Run the dashboard
uv run marimo edit app.py
# or via CLI:
uv run psychoanalyze marimo
```

## Specs, Contracts, and Diagrams

This repo treats implementation as downstream of declarative artifacts (see `docs/plan-engineeringApproach.prompt.md`):

- **System map**: `docs/plan.d2` is the top-level dependency/order graph.
- **Data contract**: `data-contract.odcs.yaml` is the schema-level boundary (validated via `datacontract-cli`, wired through `prek.toml`).
- **Acceptance specs (BDD)**:
  - Source specs live in `features/*.feature` and `docs/*.feature`.
  - Executable pytest-bdd step definitions live under `tests/bdd-features/`.
- **Diagrams**: D2 sources in `docs/*.d2`, rendered into `docs/figures/`.
  - Prefer VS Code tasks for watch/render workflows (e.g. “D2: Watch all diagrams”).

## Testing and Reporting

- **Allure**: pytest is configured with `--alluredir=allure-results`.
- **Local dashboard**: run `allure serve` (or the workspace task) to browse results.
- **Markers**: prefer pytest markers (`unit`, `integration`, `slow`, `data`, `analysis`, etc.) for test organization.

## Code Conventions

### Type Annotations
- Prefer broad input types, narrow output types
- Use builtin generics: `list[str]`, `dict[str, int]`, not `List`, `Dict`
- Use `|` for unions, not `Optional` or `Union`

### Tabular Data Patterns
- Prefer **Polars** (`polars.DataFrame`) for core transforms; convert to Pandas only at presentation boundaries (e.g., Plotly Express).
- Validation/type-shapes live primarily in `src/psychoanalyze/types.py` (Patito + Pydantic models).
- Index columns: `Intensity`, `Block`, multi-indexes for sessions
- Standard column names: `Result` (0/1), `Hits`, `Hit Rate`, `n trials`

### Plotly Usage
- Use global template from `plot.template` for consistent styling
- Subject colormap: `{"U": "#e41a1c", "Y": "#377eb8", "Z": "#4daf4a"}`
- Return `go.Figure` objects, use `px` for quick plots

### Testing
Tests mirror source structure in `tests/`. Use pytest fixtures for common data:
```python
import polars as pl

@pytest.fixture()
def trials_df() -> pl.DataFrame:
  return pl.DataFrame({"Intensity": [...], "Result": [...], "Block": [...]})
```

## Key Formulas Reference

```python
# Threshold from logistic fit params
threshold = -intercept / slope  # x₀ = -b₀/b₁

# Generate stimulus range from model params
min_x = (logit(0.01) - intercept) / slope
max_x = (logit(0.99) - intercept) / slope
```
