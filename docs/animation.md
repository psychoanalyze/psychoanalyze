# PyMC Sampling Animation

This module provides animation capabilities for PyMC MCMC sampling, allowing users to visualize the evolution of the posterior distribution with pause and rewind functionality.

## Features

- **Full Sampling Control**: Sample the complete posterior with snapshot capture
- **Rewind to Any Draw**: Navigate to any point in the sampling process
- **Multiple Visualizations**: Trace plots, posterior distributions, psychometric curves
- **Multi-Chain Support**: Visualize and compare multiple MCMC chains
- **Save/Load Snapshots**: Persist sampling state for later replay

## Quick Start

```python
import polars as pl
from psychoanalyze.animation import AnimatedSampler
from psychoanalyze.animation.plot import plot_sampling_dashboard

# Prepare trial data
trials_df = pl.DataFrame({
    "Intensity": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
    "Result": [0, 0, 0, 1, 1, 1, 1],
})

# Create animated sampler
sampler = AnimatedSampler(
    trials=trials_df,
    draws=500,
    tune=500,
    chains=2,
    random_seed=42,
)

# Sample with snapshots
idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=25)

# Visualize at a specific draw
fig = plot_sampling_dashboard(
    sampler,
    trials=trials_df,
    up_to_draw=250,
    chain=0,
)
fig.show()
```

## Core Components

### AnimatedSampler

The `AnimatedSampler` class wraps PyMC's sampling functionality to enable animation:

```python
sampler = AnimatedSampler(
    trials: pl.DataFrame,        # Trial data with Intensity and Result columns
    draws: int = 1000,            # Number of posterior samples per chain
    tune: int = 1000,             # Number of tuning steps
    chains: int = 2,              # Number of MCMC chains
    cores: int = 1,               # CPU cores to use
    target_accept: float = 0.9,   # Target acceptance rate
    random_seed: int | None = None,
)
```

### Key Methods

#### Sample with Snapshots

```python
idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=10)
```

Samples the full posterior and creates snapshots at regular intervals. Each snapshot contains:
- Draw number
- Chain number
- Posterior samples up to that draw
- Acceptance rate

#### Rewind to Specific Draw

```python
snapshot = sampler.rewind_to(draw=100, chain=0)
```

Navigate to a specific point in the sampling process. Returns the snapshot at that draw.

#### Get Parameter Evolution

```python
df = sampler.get_parameter_evolution(param_name="threshold", chain=0)
```

Returns a DataFrame with the evolution of a parameter across draws.

#### Save/Load Snapshots

```python
# Save
sampler.save_snapshots(Path("./snapshots"))

# Load
sampler.load_snapshots(Path("./snapshots"))
```

Persist sampling state to disk for later replay.

## Visualization Functions

The `psychoanalyze.animation.plot` module provides several visualization functions:

### Trace Evolution

```python
from psychoanalyze.animation.plot import plot_trace_evolution

fig = plot_trace_evolution(
    sampler,
    param_name="threshold",
    chain=0,
    up_to_draw=250,
)
```

Shows how a parameter's trace evolves over draws.

### Posterior Distribution Evolution

```python
from psychoanalyze.animation.plot import plot_posterior_evolution

fig = plot_posterior_evolution(
    sampler,
    param_name="threshold",
    chain=0,
    up_to_draw=250,
)
```

Displays the posterior distribution as it builds up.

### Psychometric Curve Evolution

```python
from psychoanalyze.animation.plot import plot_psychometric_curve_evolution

fig = plot_psychometric_curve_evolution(
    sampler,
    trials=trials_df,
    up_to_draw=250,
    chain=0,
    n_curves=50,
)
```

Shows how the fitted psychometric curve evolves with uncertainty bands.

### Multi-Chain Traces

```python
from psychoanalyze.animation.plot import plot_multi_chain_traces

fig = plot_multi_chain_traces(
    sampler,
    param_name="threshold",
    up_to_draw=250,
)
```

Displays traces for all chains to visualize convergence.

### Comprehensive Dashboard

```python
from psychoanalyze.animation.plot import plot_sampling_dashboard

fig = plot_sampling_dashboard(
    sampler,
    trials=trials_df,
    up_to_draw=250,
    chain=0,
)
```

All-in-one view with traces, posteriors, and fitted curves.

## Interactive Example

See `examples/sampling_animation_demo.py` for a complete interactive marimo notebook demonstrating all features with sliders for draw selection and chain navigation.

## Use Cases

1. **Educational**: Teach MCMC concepts by showing real-time sampling evolution
2. **Diagnostic**: Identify sampling issues by examining early convergence behavior
3. **Publication**: Create animated figures showing Bayesian inference in action
4. **Research**: Analyze how different priors affect sampling trajectories

## Technical Details

### Snapshot Storage

Snapshots are stored as `SamplerSnapshot` dataclasses containing:
- `draw`: Draw number (0-indexed)
- `chain`: Chain number
- `posterior_samples`: Dict of parameter samples
- `acceptance_rate`: Acceptance rate up to this draw

### Memory Considerations

Snapshots store cumulative posterior samples, so memory usage increases with:
- Number of snapshots (`draws / snapshot_interval`)
- Number of parameters (3 in psychometric model: intercept, slope, threshold)
- Number of chains

For large sampling runs, increase `snapshot_interval` to reduce memory usage.

### Integration with Existing Code

The `AnimatedSampler` uses the same PyMC model structure as `trials.fit()` and `blocks.fit()`, ensuring consistency with existing psychoanalyze functionality.

## Advanced Usage

### Custom Snapshot Intervals

```python
# Fine-grained snapshots (more memory)
idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=5)

# Coarse-grained snapshots (less memory)
idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=50)
```

### Accessing Raw Trace Data

```python
# Get all traces
traces = sampler.get_trace_data()

# Get traces up to specific draw
traces_partial = sampler.get_trace_data(up_to_draw=100)

# Access individual parameters
intercepts = traces["intercept"]  # Shape: (chains, draws)
slopes = traces["slope"]
thresholds = traces["threshold"]
```

### Chain-Specific Snapshots

```python
# Get all snapshots for a specific chain
chain_0_snapshots = sampler.get_snapshots_for_chain(chain=0)

# Access specific snapshot
snapshot = sampler.get_snapshot(draw=100, chain=0)
if snapshot is not None:
    print(f"Threshold samples: {len(snapshot.posterior_samples['threshold'])}")
```

## Future Enhancements

Potential future additions:
- Real-time streaming visualization during sampling
- Interactive animation controls (play/pause/rewind UI component)
- Comparison mode for different sampling configurations
- Export animations as videos or GIFs
- Integration with ArviZ for advanced diagnostics
