# Animation System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PsychoAnalyze Animation                     │
└─────────────────────────────────────────────────────────────────┘

                    User Input: Trial Data
                             │
                             ▼
         ┌──────────────────────────────────────┐
         │      AnimatedSampler.__init__()      │
         │  - Build PyMC model                  │
         │  - Initialize state tracking         │
         └──────────────────────────────────────┘
                             │
                             ▼
         ┌──────────────────────────────────────┐
         │   sample_with_snapshots(interval)    │
         │  1. pm.sample() → InferenceData      │
         │  2. Extract snapshots at intervals   │
         │  3. Store in memory                  │
         └──────────────────────────────────────┘
                             │
                             ▼
         ┌──────────────────────────────────────┐
         │           InferenceData              │
         │  + List[SamplerSnapshot]             │
         └──────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    ┌────────┐         ┌────────┐         ┌────────┐
    │ rewind │         │  get   │         │  save  │
    │   _to  │         │snapshot│         │snapshot│
    └────────┘         └────────┘         └────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
         ┌──────────────────────────────────────┐
         │      Visualization Functions         │
         │                                      │
         │  • plot_trace_evolution()           │
         │  • plot_posterior_evolution()       │
         │  • plot_psychometric_curve_...()   │
         │  • plot_multi_chain_traces()       │
         │  • plot_sampling_dashboard()       │
         └──────────────────────────────────────┘
                             │
                             ▼
         ┌──────────────────────────────────────┐
         │      Interactive Marimo App          │
         │                                      │
         │  ┌────────────────────────────┐     │
         │  │  Draw Slider [0───●───500] │     │
         │  └────────────────────────────┘     │
         │  ┌────────────────────────────┐     │
         │  │  Chain Selector  [Chain 0▼]│     │
         │  └────────────────────────────┘     │
         │                                      │
         │  ┌────────────────────────────┐     │
         │  │    Trace Plot              │     │
         │  │    ┌────────────┐          │     │
         │  │    │    /\  /\  │          │     │
         │  │    │   /  \/  \ │          │     │
         │  │    └────────────┘          │     │
         │  └────────────────────────────┘     │
         │                                      │
         │  ┌────────────────────────────┐     │
         │  │  Posterior Histogram       │     │
         │  │  ┌────────────┐            │     │
         │  │  │  ┌──┐      │            │     │
         │  │  │┌─┼──┼──┐   │            │     │
         │  │  └──────────┘              │     │
         │  └────────────────────────────┘     │
         │                                      │
         │  ┌────────────────────────────┐     │
         │  │  Psychometric Curve        │     │
         │  │  ┌────────────┐            │     │
         │  │  │      ┌───  │            │     │
         │  │  │    ┌─┘     │            │     │
         │  │  └────────────┘            │     │
         │  └────────────────────────────┘     │
         └──────────────────────────────────────┘
```

## Data Flow

```
Trial Data (Polars DataFrame)
    │
    ├─ Intensity: [0.0, 0.5, 1.0, ...]
    └─ Result:    [0,   0,   1,   ...]
    │
    ▼
PyMC Model (Bayesian Logistic Regression)
    │
    ├─ intercept ~ Normal(0, 2.5)
    ├─ slope     ~ Normal(0, 2.5)
    └─ threshold = -intercept / slope
    │
    ▼
MCMC Sampling (NUTS Algorithm)
    │
    ├─ Tune:  1000 samples (discarded)
    ├─ Draw:  1000 samples (kept)
    └─ Chains: 2 parallel chains
    │
    ▼
InferenceData (ArviZ format)
    │
    ├─ posterior
    │   ├─ intercept: [chains=2, draws=1000]
    │   ├─ slope:     [chains=2, draws=1000]
    │   └─ threshold: [chains=2, draws=1000]
    │
    └─ sample_stats
        ├─ diverging
        ├─ energy
        └─ acceptance_rate
    │
    ▼
Snapshots (List[SamplerSnapshot])
    │
    ├─ Snapshot 0  (draw=0,   chain=0)
    │   └─ posterior_samples: {intercept: [1],  slope: [1],  ...}
    │
    ├─ Snapshot 1  (draw=25,  chain=0)
    │   └─ posterior_samples: {intercept: [26], slope: [26], ...}
    │
    ├─ Snapshot 2  (draw=50,  chain=0)
    │   └─ posterior_samples: {intercept: [51], slope: [51], ...}
    │
    └─ ... (configurable intervals)
    │
    ▼
User Interaction
    │
    ├─ Slider: Move to draw=250
    │   └─ Triggers: rewind_to(250, chain=0)
    │       └─ Returns: Snapshot at draw=250
    │
    ├─ Dropdown: Select Chain 1
    │   └─ Triggers: Rerender with chain=1
    │
    └─ Auto-refresh: All plots update reactively
```

## Snapshot Structure

```python
@dataclass
class SamplerSnapshot:
    draw: int                              # e.g., 250
    chain: int                             # e.g., 0
    posterior_samples: dict[str, ndarray]  # e.g., {
                                           #   "intercept": array([...]),  # shape: (250,)
                                           #   "slope":     array([...]),  # shape: (250,)
                                           #   "threshold": array([...])   # shape: (250,)
                                           # }
    acceptance_rate: float                 # e.g., 0.92
```

## Visualization Pipeline

```
Snapshot (draw=250, chain=0)
    │
    ├─ Extract: posterior_samples["threshold"][:250]
    │   │
    │   ├─ plot_trace_evolution()
    │   │   └─ Line plot: x=draws, y=threshold values
    │   │
    │   └─ plot_posterior_evolution()
    │       └─ Histogram: distribution of threshold values
    │
    ├─ Extract: posterior_samples["intercept"][:250]
    │           posterior_samples["slope"][:250]
    │   │
    │   └─ plot_psychometric_curve_evolution()
    │       └─ Scatter + Lines: fitted curves with uncertainty
    │
    └─ Extract: All chains up to draw=250
        │
        └─ plot_multi_chain_traces()
            └─ Multiple lines: one per chain
```

## State Management

```
AnimatedSampler State Machine
    │
    ├─ IDLE
    │   └─ Initial state, no sampling done
    │
    ├─ SAMPLING  (not used in current implementation)
    │   └─ Would be used for real-time sampling
    │
    ├─ PAUSED    (not used in current implementation)
    │   └─ Would be used for real-time sampling
    │
    └─ COMPLETED
        └─ Sampling finished, snapshots available
            │
            ├─ current_draw:  Tracks navigation position
            ├─ current_chain: Tracks selected chain
            └─ snapshots:     List of all snapshots
```

## Memory Layout

```
InferenceData: ~5 MB
    ├─ posterior["intercept"]: (2 chains × 1000 draws × 8 bytes) = 16 KB
    ├─ posterior["slope"]:     (2 chains × 1000 draws × 8 bytes) = 16 KB
    ├─ posterior["threshold"]: (2 chains × 1000 draws × 8 bytes) = 16 KB
    └─ metadata + sample_stats: ~5 MB

Snapshots: ~2 MB (40 snapshots × 50 KB each)
    ├─ Each snapshot stores cumulative samples
    ├─ Memory grows linearly with n_snapshots
    └─ Trade-off: Finer granularity vs. memory usage

Total: ~7 MB for typical use case
```

## File System Layout

```
psychoanalyze/
├── src/psychoanalyze/
│   └── animation/
│       ├── __init__.py          (exports)
│       ├── sampler.py           (AnimatedSampler class)
│       └── plot.py              (visualization functions)
│
├── tests/
│   └── test_animation.py        (12 test cases)
│
├── examples/
│   └── sampling_animation_demo.py  (marimo notebook)
│
├── docs/
│   └── animation.md             (comprehensive guide)
│
├── IMPLEMENTATION.md            (technical details)
└── README.md                    (updated with feature)
```
