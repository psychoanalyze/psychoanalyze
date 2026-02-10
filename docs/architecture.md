# PsychoAnalyze Architecture

This document explains the three-pillar architecture of PsychoAnalyze, which organizes all features and capabilities around three core purposes.

## Architecture Overview

![Architecture Diagram](./figures/architecture.svg)

PsychoAnalyze is structured around **three independent but interconnected pillars**:

### 1. Real-time/Online Data Processing

The **data processing pillar** handles all computational aspects of psychophysical data transformation and analysis:

- **PsychoPy Integration**: Stream trial data from live experiments with adaptive threshold estimation
- **Data Pipeline**: Transform raw trials through the data hierarchy (trials → points → blocks → sessions)
- **Modeling**: Fit psychometric curves, Weber power laws, strength-duration relationships, and Bayesian hierarchical models
- **Validation**: Enforce data contracts and schema compliance with Pandera
- **Batch Processing**: Handle large-scale offline analysis with parallel execution

**Key capabilities:**
- Online trial aggregation and real-time psychometric fitting
- Advanced statistical models (Weber, strength-duration, Bayesian hierarchical)
- Data quality assurance and type safety
- Scalable batch processing for multi-subject datasets

### 2. Interactive Dashboard & Bayesian Workflow

The **dashboard pillar** provides a reactive web interface for data exploration and Bayesian model building:

- **Marimo App**: Reactive notebook (app.py) with persistent UI state
- **Visualization Suite**: 5 core plot types (psychometric, threshold-time, Weber, strength-duration, Bayesian diagnostics)
- **Interactive Controls**: Scale toggles, unit conversion, subject filters, parameter inputs
- **Gelman Bayesian Workflow**: Complete implementation of the principled Bayesian workflow
  - Prior setup and predictive checks
  - MCMC fitting with live monitoring
  - Convergence diagnostics (R-hat, ESS, trace plots)
  - Posterior predictive checks
  - Model comparison (WAIC, LOO-CV)
  - Sensitivity analysis and shrinkage visualization

**Key capabilities:**
- Real-time MCMC monitoring with auto-refreshing diagnostics
- Comprehensive Bayesian workflow from prior elicitation to model comparison
- Interactive plot controls for exploration
- Export reports and posterior samples

### 3. Ergonomic Python Package

The **Python API pillar** enables custom scripting, automation, and programmatic access:

- **Library Structure**: Well-organized modules (`data/`, `analysis/`, utils)
- **High-Level API**: Simple functions for common tasks (`.fit()`, `.plot()`, `.analyze()`)
- **Scripting Patterns**: Support for automation, Jupyter notebooks, CI integration
- **CLI**: Command-line interface for shell-based workflows
- **Developer Experience**: Full type hints, docstrings, clear error messages

**Key capabilities:**
- One-line psychometric fitting: `psychoanalyze.fit(trials_df)`
- Seamless Pandas/Polars/NumPy integration
- Extensible design for custom models and priors
- Version-controlled reproducible analysis scripts
- Batch CLI commands for pipeline orchestration

## Cross-Pillar Interactions

The three pillars are **loosely coupled** but work together seamlessly:

1. **Data Processing → Dashboard**: Pipeline produces DataFrames that feed the dashboard
2. **Dashboard → Python API**: Dashboard imports and uses the library's PyMC models and fitting functions
3. **Python API → Data Processing**: API provides programmatic control over pipelines
4. **PsychoPy → Package**: Real-time experiment data can be exported for scripting
5. **CLI → Batch Processing**: Command-line tools orchestrate large-scale pipelines
6. **Dashboard → Library**: Plotting uses the shared `plot.py` template

This architecture ensures:
- **Separation of concerns**: Each pillar has a clear, independent purpose
- **Flexibility**: Use one pillar without the others (e.g., Python API in isolation)
- **Consistency**: Shared data contracts and schemas across all pillars
- **Maintainability**: Changes to one pillar rarely break others

## Feature Scenarios by Pillar

### Real-time/Online Data Processing
- Stream trials from PsychoPy experiments
- Adaptive staircase threshold estimation
- Online trial → points aggregation
- Logistic regression fitting (x₀, k estimation)
- Longitudinal session joining
- Intensity scale transformations (log, z-score, Weber)
- Weber power-law modeling (JND = k × I^n)
- Strength-duration curve fitting
- Hierarchical Bayesian models (PyMC)
- Pandera schema validation
- Missing data detection
- Outlier flagging
- Batch CSV/Parquet/HDF5 import
- Parallel execution (Dask/Joblib)
- Parameter export

### Interactive Dashboard & Bayesian Workflow
- Reactive Marimo notebook interface
- File upload and sample data loading
- 5 core visualization types
- Scale controls (linear/log)
- Unit switchers (mA/μC, ms/μs)
- Subject filtering (U, Y, Z)
- Date range selection
- Prior definition (x₀, k, λ, γ)
- Hierarchical model configuration
- Prior predictive checks
- MCMC sampler configuration
- PyMC inference execution
- Live sampling progress
- Divergence/convergence warnings
- Trace plots
- R-hat convergence checks
- Effective sample size (ESS) checks
- Posterior density plots
- Posterior predictive checks
- Bayesian p-values
- Model comparison (WAIC, LOO-CV)
- Sensitivity analysis
- Shrinkage visualization
- PDF report generation
- Posterior sample export (NetCDF/CSV)
- Subject-level parameter exploration

### Ergonomic Python Package
- `psychoanalyze.fit()` for one-line fitting
- `psychoanalyze.plot.*` quick plotting utilities
- `psychoanalyze.analyze.*` statistical pipelines
- Batch processing scripts
- Cron job integration
- CI/CD test integration
- Jupyter notebook support
- Reproducible analysis scripts
- Publication-quality figure generation
- Model subclassing and extension
- Custom prior definitions
- Algorithm A/B testing
- Pandas DataFrame interop
- Polars DataFrame support
- NumPy array inputs
- CSV/Parquet/HDF5 I/O
- CLI commands (`psychoanalyze fit`, `psychoanalyze plot`)
- TOML/YAML configuration
- Pipeline orchestration
- Full type annotations
- NumPy-style docstrings
- Helpful error messages
- Example scripts

## Potential Future Features

The diagram also identifies potential enhancements:

- **REST API**: Flask/FastAPI server for web integration
- **Standalone Web App**: Svelte/React frontend (decoupled from Python)
- **Cloud Deployment**: AWS Lambda, Fly.io hosting
- **Database Backend**: PostgreSQL or DuckDB for persistence
- **ML Integration**: scikit-learn pipeline compatibility
- **Mobile App**: Companion app for trial collection
- **Collaborative Mode**: Shared sessions across researchers
- **Version Control**: DVC or Git-tracked analysis versioning
- **Plugin System**: Custom link functions and model types

## Usage Patterns

### For Experimentalists (Dashboard)
```bash
uv run marimo edit app.py
# Upload data, explore plots, run Bayesian workflow
```

### For Scripters (Python API)
```python
import psychoanalyze as psy

# Load data
trials = psy.data.load_trials("experiment.csv")

# Fit psychometric function
points = psy.fit(trials)

# Plot results
fig = psy.plot.psychometric(points)
fig.show()

# Run Bayesian analysis
posterior = psy.analyze.bayesian(points, prior_config=...)
```

### For Production Pipelines (CLI + Batch)
```bash
# Batch process all subjects
psychoanalyze fit data/*.csv --output results/

# Generate all plots
psychoanalyze plot results/*.parquet --format png

# Run full Bayesian workflow
psychoanalyze analyze results/ --workflow bayesian --export pdf
```

## Viewing the Diagram

To view the architecture diagram interactively:

1. **Watch mode** (auto-updates on changes):
   ```bash
   # Watch all diagrams
   nu scripts/plan/watch_all_d2.nu

   # Or use VS Code task
   Cmd+Shift+P → "Tasks: Run Task" → "D2: Watch all diagrams"
   ```

2. **One-time render**:
   ```bash
   d2 docs/architecture.d2 docs/figures/architecture.svg
   xdg-open docs/figures/architecture.svg

   # Or use VS Code task
   Cmd+Shift+P → "Tasks: Run Task" → "D2: Render and view architecture diagram"
   ```

## Related Documentation

- [Data Pipeline Feature Specs](./data-pipeline.feature) - BDD scenarios for data processing
- [Gelman Workflow Feature Specs](./gelman-workflow.feature) - Detailed Bayesian workflow scenarios
- [Data Contract](../data-contract.odcs.yaml) - Schema definitions and validation rules
- [Plot Diagrams](./figures/) - Individual plot type specifications
- [Original Plan](./plan.d2) - Detailed TDD revision planning

---

**Last Updated**: 2026-02-06
