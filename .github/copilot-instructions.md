# PsychoAnalyze - Copilot Instructions

## Project Overview

PsychoAnalyze is a Python library for interactive data simulation and analysis in psychophysics research. It models psychometric functions using logistic regression to estimate detection thresholds from experimental trial data.

## Architecture

### Data Hierarchy (core concept)
The codebase follows a strict hierarchical data model where each level aggregates the one below:
1. **Trials** (`data/trials.py`) - Individual stimulus presentations (Intensity, Result)
2. **Points** (`data/points.py`) - Aggregated trial counts at each intensity (Hit Rate = Hits / n trials)
3. **Blocks** (`data/blocks.py`) - Fitted psychometric curves (threshold + slope from logistic regression)
4. **Sessions/Subjects** - Longitudinal groupings

Each module in `src/psychoanalyze/data/` corresponds to one level. Functions typically transform data upward (e.g., `trials.fit()` → block params).

### Key Components
- **`app.py`** - Marimo notebook serving as the interactive dashboard (replaces former Dash app)
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

```bash
# Package management (uv only, not pip)
uv sync                      # Install dependencies
uv run pytest                # Run tests
uv run ruff check --fix      # Lint and autofix
uv run ty check              # Type check (uses ty, not mypy)

# Run the dashboard
uv run marimo edit app.py
# or via CLI:
uv run psychoanalyze marimo
```

## Code Conventions

### Type Annotations
- Prefer broad input types, narrow output types
- Use builtin generics: `list[str]`, `dict[str, int]`, not `List`, `Dict`
- Use `|` for unions, not `Optional` or `Union`

### Pandas Patterns
- Data schemas defined in `data/types.py` using Pandera
- Index columns: `Intensity`, `Block`, multi-indexes for sessions
- Standard column names: `Result` (0/1), `Hits`, `Hit Rate`, `n trials`

### Plotly Usage
- Use global template from `plot.template` for consistent styling
- Subject colormap: `{"U": "#e41a1c", "Y": "#377eb8", "Z": "#4daf4a"}`
- Return `go.Figure` objects, use `px` for quick plots

### Testing
Tests mirror source structure in `tests/`. Use pytest fixtures for common data:
```python
@pytest.fixture()
def trials_df() -> pd.DataFrame:
    return pd.DataFrame({"Intensity": [...], "Result": [...], "Block": [...]})
```

## Key Formulas Reference

```python
# Threshold from logistic fit params
threshold = -intercept / slope  # x₀ = -b₀/b₁

# Generate stimulus range from model params
min_x = (logit(0.01) - intercept) / slope
max_x = (logit(0.99) - intercept) / slope
```

## Copilot Skills

### D2 Diagram Generation
The project includes a Copilot skill for generating D2 diagrams. See `.github/skills/` for details.

Available diagram types:
- **Data Hierarchy**: Shows Trials → Points → Blocks → Sessions transformation
- **Module Architecture**: Component relationships and interactions
- **Analysis Workflow**: Data flow through processing and analysis pipelines
- **Psychometric Function**: Formula components and computation steps

Example usage: "Generate a D2 diagram of the data hierarchy" or "Show me an architecture diagram in D2"

Example diagrams are available in `.github/skills/diagrams/`
