---
name: jj-tdd-revisions
description: Guide for working through PsychoAnalyze's TDD-based jj revisions, implementing the data pipeline, plots, contract validation, and Bayesian workflow in a structured red/green/refactor cycle. Use when building features from the plan, running test-first development with jj, or coordinating multi-step feature implementation.
compatibility: Requires jj (Jujutsu version control), Python with pytest, and uv package manager for PsychoAnalyze project
metadata:
  author: PsychoAnalyze Team
  version: "1.0"
  domain: psychophysics-data-analysis
---

# JJ TDD Revisions Workflow

## Overview

This skill guides you through the phased, test-first implementation of PsychoAnalyze features using Jujutsu (jj) revisions. Each revision represents one unit of work following the **Red → Green → Refactor** cycle:

- **Red**: Write failing tests describing desired behavior
- **Green**: Implement minimal code to make tests pass
- **Refactor**: Improve code quality, security, and design

## Revision Dependency Graph

The workflow follows this sequence (each node = one Red/Green/Refactor cycle):

```
main
  └── data_schema (schema + contract)
       ├── trial_aggregation (trials → points)
       ├── psychometric_fit (logistic fit → blocks)
       ├── intensity_scaling (log / z-score views)
       ├── longitudinal_join (blocks + sessions join)
       ├── weber_fit (Weber power-law fit)
       ├── sd_fit (strength-duration fit)
       └── bayes_model (PyMC hierarchical model)
            └── contract_validation (pandera schema check)
                 ├── psych_plot (psychometric plot)
                 ├── threshold_plot (threshold vs time plot)
                 ├── weber_plot (Weber plot)
                 ├── sd_plot (S-D plot)
                 ├── bayes_plot (posterior diagnostics plot)
                 └── plot_controls (scale/unit toggles)
                      └── bayesian_workflow (full Gelman workflow)
                           └── docs (docs + examples)
```

### Data Pipeline Stages

1. **data_schema**: Define Pandera schemas for all tables (Trials, Points, Blocks, Sessions)
2. **trial_aggregation**: Aggregate individual trials into point-level hit rates
3. **psychometric_fit**: Fit logistic regression to estimate thresholds
4. **intensity_scaling**: Generate log-scale and z-score normalized stimulus views
5. **longitudinal_join**: Join blocks to sessions for multi-session analysis
6. **weber_fit**: Apply Weber's power-law model to threshold ratios
7. **sd_fit**: Fit strength-duration curves for pulse-width effects

### Validation & Plotting

8. **contract_validation**: Verify all outputs comply with data contract
9-14. **Plot functions**: Render psychometric, threshold, Weber, S-D, and Bayes diagnostic plots
15. **plot_controls**: Implement unit/scale toggles in the Marimo dashboard

### Analysis

16. **bayesian_workflow**: Implement full Gelman Bayesian workflow (priors, MCMC, diagnostics)
17. **docs**: Generate API documentation and tutorial examples

---

## Red Phase: Writing Failing Tests

Before implementing any feature, write tests that describe the desired behavior.

### Test File Locations

Tests mirror source structure in `tests/`:
```
tests/
├── test_psi.py                    # Psychometric function tests
├── data/
│   ├── test_trials.py             # Trial aggregation
│   ├── test_blocks.py             # Psychometric fitting
│   ├── test_points.py             # Hit rate calculations
│   ├── test_sessions.py           # Longitudinal joins
│   ├── test_logistic.py           # Logistic regression
│   └── test_types.py              # Schema validation
├── analysis/
│   ├── test_weber.py              # Weber power-law
│   ├── test_strength_duration.py  # S-D curves
│   ├── test_bayes.py              # Bayesian inference
│   └── test_ecdf.py               # ECDF analysis
└── visualization/
    └── test_plot.py               # Plot generation & controls
```

### Example Test Structure

```python
import pytest
import pandas as pd
from psychoanalyze.data.blocks import fit

@pytest.fixture()
def trials_df() -> pd.DataFrame:
    """Create sample trials data for testing."""
    return pd.DataFrame({
        "Intensity": [10, 20, 30, 10, 20, 30],
        "Result": [0, 0, 1, 0, 1, 1],
        "Block": [1, 1, 1, 2, 2, 2],
    })

def test_psychometric_fit_returns_threshold(trials_df):
    """Given trial data, should return threshold estimate."""
    block_params = fit(trials_df)

    assert "x0" in block_params.columns  # threshold
    assert "k" in block_params.columns   # slope
    assert not block_params["x0"].isna().any()
```

### BDD Scenarios (Feature Files)

Reference these for acceptance criteria:
- [data-pipeline.feature](../../docs/data-pipeline.feature) - Data processing scenarios
- [gelman-workflow.feature](../../docs/gelman-workflow.feature) - Bayesian analysis workflow

---

## Green Phase: Minimal Implementation

Write the simplest code that makes tests pass. Focus on correctness, not optimization.

### Common JJ Commands

```bash
# Create a new revision for this phase
jj new -m "trial-aggregation: red phase - write failing tests"

# Edit the working copy (shorthand for jj edit @)
jj edit @

# Make changes, then run tests
uv run pytest tests/data/test_trials.py -v

# Once tests pass, commit
jj commit -m "trial-aggregation: green phase - implement trials.aggregate()"

# Check revision history
jj log
```

### Data Processing Pattern

Most PsychoAnalyze functions follow this pattern:

```python
def aggregate(trials_df: pd.DataFrame) -> pd.DataFrame:
    """Transform trials into points with hit rate aggregation.

    Input columns: Intensity, Result, Block
    Output columns: Intensity, (Hit Rate | Hits | n trials), Block
    """
    # 1. Validate input schema
    # 2. Group and aggregate
    # 3. Validate output schema
    # 4. Return result
```

### Pandas Conventions

- Use Pandera schemas from `data/types.py` for validation
- Index by `Intensity` and/or `Block` where hierarchical makes sense
- Standard column names: `Result` (0/1), `Hits`, `Hit Rate`, `n trials`
- Multi-index for sessions: `(Block, Session)` or `(Block, Subject)`

---

## Refactor Phase: Quality & Design

Improve code quality while keeping tests green.

### Refactoring Checklist

- [ ] Type hints complete and correct
- [ ] Function docstrings follow NumPy style
- [ ] Pandera schema validation in place
- [ ] Edge cases documented (empty DataFrames, single value, etc.)
- [ ] Variable names self-explanatory (no `tmp_df`, `x`, `df2`)
- [ ] Comments explain WHY, not WHAT
- [ ] Security properties verified (no SQL injection, etc.)
- [ ] Performance acceptable (profile if slow)
- [ ] Tests cover edge cases (empty, boundary, invalid input)

### Example Refactor Commit

```bash
jj commit -m "trial-aggregation: refactor - improve types, edge cases, docs"
```

### Type Annotation Guidelines

```python
# Prefer broad inputs, narrow outputs
def aggregate(trials_df: pd.DataFrame) -> pd.DataFrame:
    # ✓ Accept any DataFrame, return validated one
    pass

# Use builtin generics (Python 3.9+)
def get_subjects(sessions: dict[str, int]) -> list[str]:
    # ✓ dict[str, int], not Dict[str, int]
    pass

# Union types with |
def convert_units(value: float | str) -> float:
    # ✓ float | str, not Optional[float] or Union[float, str]
    pass
```

### Bayesian Model Patterns

For MCMC sampling (weber, strength-duration, hierarchical models):

```python
# Use stan string or PyMC model definition
def fit_bayesian_model(data_df: pd.DataFrame, prior_config: dict) -> az.InferenceData:
    """Fit hierarchical Bayesian model.

    Returns ArviZ InferenceData with posterior samples.
    """
    # 1. Configure prior distributions
    # 2. Build PyMC model
    # 3. Sample from posterior
    # 4. Validate convergence (R-hat < 1.01, ESS > 400)
    # 5. Return inference object
```

---

## Working with Each Revision

### Starting a New Revision

1. **Create the revision**
   ```bash
   jj new main -m "<revision-name>: red phase - <brief description>"
   ```

2. **Write failing tests**
   - Create test file in `tests/`
   - Configure test fixtures (sample data, mock objects)
   - Write assertions matching the feature file scenarios
   - Run tests: `uv run pytest tests/<file>.py -v`

3. **Commit the red phase**
   ```bash
   jj commit -m "<revision-name>: red phase - failing tests for <feature>"
   ```

### Implementing the Feature

4. **Make tests pass** (Green phase)
   - Implement minimal code in `src/psychoanalyze/`
   - Run tests frequently: `uv run pytest`
   - Commit: `jj commit -m "<revision-name>: green phase - implement <feature>()"`

5. **Refactor for quality** (Refactor phase)
   - Apply type annotations
   - Improve docstrings and comments
   - Add edge case handling
   - Commit: `jj commit -m "<revision-name>: refactor - <improvements>"`

### Testing the Full Pipeline

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests for one module
uv run pytest tests/data/ -v

# Run specific test
uv run pytest tests/data/test_trials.py::test_aggregate_returns_hit_rate -v

# With coverage
uv run pytest --cov=src/psychoanalyze --cov-report=html
```

### Linting & Type Checking

```bash
# Format code
uv run ruff check --fix src/ tests/

# Type check
uv run ty check

# View file structure during development
jj file-list -r @
```

---

## Key Data Models

### Trials Input
```python
{
    "Intensity": [10, 20, 30, ...],
    "Result": [0, 1, 1, ...],  # 0 = miss, 1 = hit
    "Block": [1, 1, 1, 2, 2, 2, ...],  # experiment block
}
```

### Points (aggregated)
```python
{
    "Intensity": [10, 20, 30],
    "Hits": [2, 3, 5],
    "n trials": [4, 4, 6],
    "Hit Rate": [0.5, 0.75, 0.833],
    "Block": [1, 1, 1],
}
```

### Block Parameters (from logistic fit)
```python
{
    "x0": [15.3],      # threshold (50% point)
    "k": [2.1],        # slope (steepness)
    "gamma": [0.0],    # guess rate
    "lambda": [0.0],   # lapse rate
    "Block": [1],
}
```

### Psychometric Function Equation
```
ψ(x) = γ + (1 - γ - λ) * F(x; x₀, k)
```
Where `F` is typically the logistic sigmoid: `1 / (1 + exp(-(x - x₀) * k))`

---

## Debugging Tips

### Test Failure Diagnosis

```bash
# Run with verbose output
uv run pytest tests/data/test_trials.py -vv -s

# Stop at first failure
uv run pytest -x

# Run only recently failed tests
uv run pytest --lf
```

### Data Validation Errors

If Pandera schema validation fails:

```python
from src.psychoanalyze.data.types import TrialsSchema

try:
    TrialsSchema.validate(df)
except SchemaError as e:
    print(e.message)  # Shows which rows/columns failed
```

### Logistic Fit Issues

```python
from src.psychoanalyze.data.logistic import fit_logistic

params = fit_logistic(points_df, method="scipy")
# If convergence fails, check:
# - Do points cover at least 3 intensity levels?
# - Are there at least 2 samples per level?
# - Does outcome span 0 to 1 (not all same)?
```

---

## Integration with MCP Tools

### Using the JJ-Helper Agent

For complex revision strategies, you can invoke the **jj-helper** agent:

```
Use the jj-helper subagent when:
- Reordering revisions (jj rebase)
- Squashing intermediate commits
- Amending previous revisions
- Handling merge conflicts
- Analyzing operation history (jj evolog)
```

### Using the TDD Phase Agents

- **TDD Red Phase Agent** – Write failing tests that describe desired behavior
- **TDD Green Phase Agent** – Implement minimal code to satisfy tests
- **TDD Refactor Phase Agent** – Improve code quality while maintaining green tests

---

## References

- **Jujutsu Documentation**: https://jj-vcs.github.io/jj/latest/
- **Project Plan**: [docs/plan.d2](../../docs/plan.d2)
- **Data Contract**: [docs/psychoanalyze-data-contract.odcs.yaml](../../docs/psychoanalyze-data-contract.odcs.yaml)
- **Feature Scenarios**: [docs/data-pipeline.feature](../../docs/data-pipeline.feature)
- **Bayesian Workflow**: [docs/gelman-workflow.feature](../../docs/gelman-workflow.feature)
- **Type Definitions**: [src/psychoanalyze/data/types.py](../../src/psychoanalyze/data/types.py)
- **Pytest Documentation**: https://docs.pytest.org/

---

## Quick Command Cheat Sheet

```bash
# Workflow commands
jj new -m "description"           # Create new revision
jj edit @                         # Edit working copy
jj commit -m "message"            # Save changes to current revision
jj log                            # View revision history
jj show @                         # View current revision details
jj evolog @                       # View evolution of revision

# Testing
uv run pytest tests/ -v           # Run all tests
uv run pytest -k test_name        # Run named test
uv run pytest --lf -v             # Run last-failed tests
uv run pytest --cov=src           # With coverage

# Linting & Type Check
uv run ruff check --fix           # Format and fix lints
uv run ty check                   # Type check

# Running the dashboard
uv run marimo edit app.py         # Interactive editor
uv run psychoanalyze marimo       # CLI command
```

---

## Next Steps

1. **Choose your starting revision** from the dependency graph
2. **Create a new jj revision**: `jj new main -m "<name>: red phase - <description>"`
3. **Write failing tests** that describe the feature
4. **Implement minimal code** to pass tests
5. **Refactor for quality**
6. **Move to the next revision** in the graph

Each complete Red→Green→Refactor cycle leaves you with a clean revision ready to build upon!
