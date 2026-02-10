# Streaming Bayesian Inference + BOED Implementation Plan

This plan synthesizes:
- The app requirements in [docs/full_model.md](full_model.md)
- The streaming inference pattern in [docs/svmc.md](svmc.md)

…and maps them onto an end-to-end stack using:
- **GenJAX** (probabilistic programming + programmable particle inference)
- **Bytewax** (distributed streaming dataflow + keyed state)
- **cross.stream (xs)** (local-first event stream store)
- **Panel** (interactive UI/dashboard)
- **Zombie** (grid-free Monte Carlo PDE solver for offline field bases / regularization)

---

## 1) North-star architecture (systems view)

### Dataflow (events in, posterior out, design recommendations back)

1. **Data capture** (experiment runtime)
   - Emits `TrialObserved` events (one per trial) into **xs**.

2. **Streaming inference** (always-on)
   - **Bytewax** dataflow reads `TrialObserved` from xs.
   - Keyed by `(subject_id, session_id)`.
   - Maintains a per-key **SVMC-style** particle state.
   - Writes `PosteriorSnapshot` + `PredictiveChecks` + `BOEDRankedStimuli` events back into xs.

3. **Interactive app** (human in loop)
   - **Panel** app subscribes to xs streams.
   - Renders maps/curves/trajectories/model-comparison + ranked next stimuli.
   - User (or safety rules) confirms a recommended stimulus.
   - UI emits `StimulusProposed` / `StimulusConfirmed` events to xs.

4. **Stimulus executor** (hardware integration)
   - Consumes `StimulusConfirmed` from xs.
   - Drives the stimulator.
   - Feeds observed outcomes back as `TrialObserved`.

### Storage strategy

- **xs is the system of record** (append-only event log): raw trials, parameter updates, posterior summaries, chosen stimuli.
- **Bytewax recovery** checkpoints inference state (fast restart), while xs retains full provenance.

---

## 2) Core modeling abstractions (aligns to full_model.md)

### Latents and parameters

Per subject (slow-changing):
- `θ_arch`: peripheral **neural architecture** parameters
  - density maps (3 mechanoreceptor categories)
  - fiber type mixture (Aβ, Aδ, …)
  - coupling between mechanoreceptor type ↔ fiber type
- `θ_field`: electric field basis coefficients / basis selection
- `θ_recruit`: recruitment nonlinearity + excitability + temporal sensitivity
- `m_cns`: discrete CNS integration hypothesis index (`H1..H4`)

Per trial / time-varying (nonstationarity):
- `a_t`: adaptation / gain drift state
- `c_t`: criterion / false-alarm drift state

Derived peripheral features (per trial):
- `M_t`: magnitude feature
- `T_t`: timing/spectral feature

Observed per trial:
- `s_t`: stimulus (8-electrode param vector + waveform/pattern/task)
- `y_t`: behavioral outcome (binary choice / continuous report)

### Generative factorization (implementation-first)

1. Drift dynamics (per trial):
- `a_t ~ p(a_t | a_{t-1})`
- `c_t ~ p(c_t | c_{t-1})`

2. Peripheral forward model:
- `(M_t, T_t) = g_peripheral(s_t; θ_arch, θ_field, θ_recruit)`

3. CNS observation model (discrete hypothesis):
- `y_t ~ p(y_t | M_t, T_t, a_t, c_t, m_cns)`

This structure is chosen to:
- keep the **peripheral geometry stable** while allowing **behavior drift**
- support **model comparison** through `m_cns`

---

## 3) SVMC-style streaming inference in GenJAX

### Why SVMC here

From [docs/svmc.md](svmc.md), the key engineering requirement is:
- **online learning** (proposal + model parameters)
- **streaming** (one observation at a time)
- **constant-ish per-step cost**

We adopt the SVMC pattern:
- maintain particles for filtering
- optimize a *trainable proposal* using gradients of `log(sum(weights))`

### Particle state (per key)

Maintain, per `(subject_id, session_id)`:
- `particles`: array of particles over `(θ_arch, θ_field, θ_recruit, m_cns, a_t, c_t, …)`
- `logw`: particle log-weights
- `proposal_params`: parameters of the learned proposal `r(·)`
- optional: a small set of optimizer state (e.g. Adam moments)

Practical split (SVMC tuning):
- `N` particles for filtering quality
- `L` particles for gradient estimates (small, e.g. 2–4)
- `NSGD` steps per timestep (e.g. 10–20; bounded by latency budget)

### GenJAX implementation sketch

1. **Generative function** defines the model transition and observation likelihood.
2. **Constraints** apply the observed `y_t` at each step.
3. **Programmable SMC** maintains traces/choice maps.
4. **Learned proposal** is a GenJAX-compatible function parameterized by `proposal_params`.

A minimal design is:
- one GenJAX model for the full latent structure
- a per-step inference kernel:
  - resample ancestors
  - propose new `a_t, c_t` and any per-trial auxiliary choices
  - update weights with observation likelihood
  - take `NSGD` gradient steps on proposal + (optionally) a subset of global parameters

### What gets learned online vs slowly

Online (fast, per timestep):
- proposal network parameters (critical for PF quality)
- drift dynamics parameters (adaptation/criterion) if needed

Slow or batched (periodic, lower frequency):
- the big peripheral parameters (`θ_arch`, `θ_field`, `θ_recruit`)
- CNS hypothesis posterior over `m_cns`

Implementation: do per-timestep SVMC updates for proposal/drift; schedule periodic “heavy” updates every K trials.

---

## 4) Zombie integration (electric field bases)

The full model wants:
- electric field represented via **learned spatial basis functions**
- optional offline PDE solvers to generate/regularize the bases

Use **Zombie** for an *offline/async pipeline* that produces basis libraries.

### Pipeline

1. Inputs:
- nerve cross-section boundary geometry (2D or 3D)
- electrode geometries / boundary conditions per electrode pattern

2. Zombie solves PDE queries (grid-free Monte Carlo), producing:
- potential/field samples at query points
- optionally gradients, depending on what the recruitment model consumes

3. Fit a compact basis:
- e.g. low-rank basis via PCA / dictionary learning on field samples
- store basis metadata + coefficients as an artifact

4. Runtime usage:
- inference uses basis functions as a fixed feature map
- `θ_field` are weights over basis functions (learned online)

### Where it runs

- Prefer separate “field-basis builder” job, not in the per-trial hot path.
- Triggered by:
  - new electrode configuration
  - new subject anatomy/geometry
  - basis refresh / improved modeling

---

## 5) cross.stream (xs) event model

xs is the shared backbone for:
- reliable ingestion
- reproducibility (append-only log)
- UI + streaming compute decoupling

### Streams (suggested)

- `trials` stream: `TrialObserved`
- `stimuli` stream: `StimulusProposed`, `StimulusConfirmed`
- `posteriors` stream: `PosteriorSnapshot`
- `design` stream: `BOEDRankedStimuli`
- `diagnostics` stream: `ParticleDiagnostics`, `PredictiveChecks`

### Event payloads (shape)

Keep events JSON-serializable, versioned, and keyed:
- `event_id`, `ts`, `subject_id`, `session_id`, `schema_version`
- `payload` with nested objects for stim params / outcomes

---

## 6) Bytewax dataflow (streaming compute)

### Keyed state machine per subject/session

Bytewax is responsible for:
- ordering trials per key
- applying the per-step SVMC update
- emitting posterior summaries and recommended stimuli

Conceptually:
- **Input**: `TrialObserved`
- **State**: `SVMCState`
- **Step**: `SVMCState = update(SVMCState, trial)`
- **Output**: derived events (posterior/design/diagnostics)

### Recovery

- Use Bytewax recovery to checkpoint `SVMCState`.
- xs remains the long-term log; on rebuild you can replay from xs.

---

## 7) BOED loop (information-optimal design)

### Candidate enumeration

From [docs/full_model.md](full_model.md), candidates are:
- pattern × amp × pulse width × frequency × duration × waveform
with safety constraints.

Implementation detail:
- candidates can be generated in UI or in the streaming worker, but scoring should live with inference (where particles are).

### Expected information gain (EIG) in a particle system

Given particles approximating current posterior:
1. For each candidate stimulus `s*`:
   - simulate a small number of outcomes `\tilde{y}` under each particle
   - update weights (or approximate) to estimate expected reduction in uncertainty over `m_cns`
2. Rank stimuli by EIG
3. Emit `BOEDRankedStimuli` to xs

A pragmatic MVP approximation:
- focus EIG on **CNS hypothesis discrimination** only (posterior over `m_cns`)
- keep peripheral parameters fixed within a short window

---

## 8) Panel app (interaction + visualization)

Panel subscribes to xs streams and renders the required views:
- inferred activation/density maps (from posterior summaries)
- strength–duration curves / iso-intensity contours
- adaptation/criterion trajectories over time
- bias/model comparison across hypotheses
- ranked next-stimulus recommendations

UI actions:
- confirm a stimulus recommendation
- optionally pin/override constraints

Implementation pattern:
- a small client that tails xs streams
- reactive objects update plots/tables on new events

---

## 9) Module breakdown (repo-facing plan)

Suggested additions under `src/psychoanalyze/`:

1. `psychoanalyze/events/`
   - event schemas + (de)serialization
   - stream names and versioning

2. `psychoanalyze/streaming/xs_io.py`
   - append and tail helpers for xs

3. `psychoanalyze/inference/genjax_model.py`
   - GenJAX generative function(s)
   - choice map conventions

4. `psychoanalyze/inference/svmc_kernel.py`
   - SVMC-style update kernel (resample/propose/weight/SGD)
   - state representation

5. `psychoanalyze/design/boed.py`
   - candidate generation + constraint filtering
   - EIG estimator

6. `psychoanalyze/field/zombie_basis.py`
   - offline basis builder + artifact loader

7. `psychoanalyze/ui/panel_app.py`
   - Panel entrypoint

8. `psychoanalyze/streaming/bytewax_flow.py`
   - Bytewax dataflow graph

---

## 10) Milestones (incremental, testable)

### Milestone A — Event plumbing + UI skeleton
- Define event schemas and write to xs
- Panel subscribes and shows raw trial table + latest posterior placeholder
- Bytewax reads trials from xs and emits a dummy `PosteriorSnapshot`

### Milestone B — Minimal streaming latent drift + observer model comparison
- Implement `a_t, c_t` drift state
- Implement CNS models `H1..H4` over `(M, T)` with a simplified peripheral feature extractor
- Particle filter tracks drift + `m_cns` posterior
- UI shows drift trajectories + model posterior

### Milestone C — SVMC proposal learning
- Add learned proposal and `log(sum(weights))` objective
- Online updates per trial with bounded cost (`N`, `L`, `NSGD`)
- Diagnostics: ESS, weight degeneracy, runtime per step

### Milestone D — Peripheral geometry + electric field basis
- Integrate field basis artifact loading
- Expand `g_peripheral` to use basis + recruitment model
- Validate on synthetic data

### Milestone E — BOED closed loop
- Candidate enumeration + safety constraints
- EIG scoring focused on `m_cns`
- UI shows ranked stimuli; emits `StimulusConfirmed`

### Milestone F — Zombie offline basis builder
- Prototype geometry + electrode BC pipeline
- Generate basis artifacts and plug into Milestone D

---

## 11) Testing and validation strategy

1. **Schema tests**
- round-trip serialization of events

2. **Deterministic replay tests**
- fixed RNG seed: replay a trial stream from xs and ensure posterior summaries match within tolerance

3. **Inference unit tests**
- synthetic model where ground truth is known
- ensure drift is recoverable and `m_cns` is discriminable under designed stimuli

4. **Streaming correctness**
- Bytewax state is keyed correctly; sessions don’t leak
- recovery checkpoint restore yields consistent continuation

5. **Performance budgets**
- per-trial update stays under latency target by tuning `N`, `L`, `NSGD`

---

## 12) Key design choices (defaults)

- **Use xs as the single source of truth**; treat everything else as derived.
- **Keep heavy PDE / basis building out of the streaming path**; Zombie runs offline/async.
- **Use SVMC primarily to learn the proposal online**; periodically update slow parameters.
- **BOED MVP targets CNS model discrimination first**; expand later to peripheral structure optimization.

---

## 13) Open questions (to lock down early)

1. Outcome type priority: binary choice only first, or must support continuous from day 1?
2. Peripheral geometry availability: do you already have nerve cross-sections/meshes per subject?
3. BOED safety constraints: who owns them (UI vs executor) and what is the policy format?
4. Latent feature design: are `M` and `T` computed deterministically from peripheral state, or probabilistically?
