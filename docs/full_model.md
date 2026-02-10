# Neural Stimulation Inference & Experimental Design App
**Requirements & Key Takeaways**

## 1. Purpose
Build an interactive, Bayesian app that:
- Infers **peripheral nerve architecture and recruitment** from stimulation + behavior.
- Separates **peripheral encoding** from **CNS integration hypotheses**.
- Actively selects **information-optimal stimuli** to discriminate models efficiently.

The scientific end-product is **formal model comparison between CNS integration hypotheses**, not just curve fitting.

---

## 2. Trial & Data Model
Each trial contains:
- **Subject, Date**
- **Stimulation parameters (per 8 electrodes)**
  - amplitude, pulse width, frequency, duration
  - waveform (square, sinusoid)
  - pattern (monopolar vs current steering/focusing)
- **Task type**
  - go/no-go, 2AFC, or continuous report
- **Outcome**
  - binary choice or continuous magnitude
- Stimulation parameters are time-indexed:
  - electrode contact(s) may vary pulse-by-pulse
  - simultaneous multi-contact pulses allowed (field shaping)

---

## 3. Peripheral Forward Model (Latent)
The app maintains a probabilistic model of peripheral activation:

### Neural Architecture
- Spatial density maps over nerve cross-section:
  - 3 mechanoreceptor categories
- Fiber types:
  - Aβ, Aδ (extendable)
- **Learned biological coupling** between mechanoreceptor type and fiber type
- Strong smoothness/low-rank priors for identifiability

### Electric Field Approximation
- Field represented via **learned spatial basis functions**
- Electrode patterns encoded as signed current vectors
- Monopolar vs steering handled by constraints on currents
- Optional **offline PDE / probabilistic PDE solvers** to generate or regularize field bases (not used online)

### Recruitment
- Nonlinear recruitment as a function of:
  - spatial field
  - fiber-type–specific excitability
  - temporal sensitivity
- Produces two key latent features per trial:
  - **Magnitude feature (M)** — integrated activation
  - **Timing/Spectral feature (T)** — temporal structure sensitivity
- Recruitment supports:
  - pulse-by-pulse contact switching (IMC-style control)
  - adaptive use of single vs multi-contact stimulation
- Forward model supports sparsity and power-aware priors on contact usage

---

## 4. Temporal Nonstationarity
The model explicitly includes:
- **Adaptation / learning** (gain drift over trials)
- **Criterion / false-alarm drift**
These dynamics are *separate* from peripheral geometry, allowing:
- stable spatial/SD structure
- drifting behavioral sensitivity or bias
- Temporal structure includes:
- pulse-sequence–dependent recruitment history
- dependence of current activation on recent activation patterns

---

## 5. CNS Integration Hypotheses (Model Comparison Target)
Competing observer models operate on peripheral features:

- **H1: Magnitude-only**
  Behavior depends only on M
- **H2: Timing-only**
  Behavior depends only on T
- **H3: Timing + magnitude bias** *(primary target)*
  Timing code modulated by magnitude
- **H4: Temporal filter-bank integration**
  Timing features passed through filters

Models are compared via:
- out-of-sample predictive performance (e.g. PSIS-LOO)
- bias signatures under orthogonal stimulus manipulations
- Sinusoidal stimuli are treated as diagnostic probes:
  - isolate temporal sensitivity and frequency tuning
  - test CNS timing-based hypotheses
- Sinusoids are not assumed to be optimal encoders

---

## 6. Fourier / Sinusoidal Stimuli (Design Principle)
- Sinusoids are treated as **frequency-domain probes**, not linear encodings.
- Used to:
  - isolate temporal sensitivity of fibers
  - design energy-matched but spectrally distinct stimuli
  - break magnitude-only CNS models
- Square pulses remain baseline; sinusoids are targeted probes.

---

## 7. Bayesian Inference Engine
Core capabilities:
- Hierarchical Bayesian inference over:
  - neural architecture
  - adaptation states
  - CNS model index
- Initial implementation: **NumPyro (SVI)**
- Scalable/advanced option: **GenJAX** for
  - programmable particle filters
  - discrete latent structure
  - heavy simulation + BOED loops

---

## 8. Information-Optimal Experimental Design (BOED)
The app runs a closed loop:
1. Fit/update posterior from observed trials
2. Enumerate candidate stimuli (pattern × amp × PW × freq × waveform)
3. Score candidates by **expected information gain**
   - especially for *CNS model discrimination*
4. Propose next stimulus (with safety constraints)

---

## 9. Visualization & Interaction
The UI should expose:
- inferred activation/density maps
- strength–duration curves and iso-intensity contours
- adaptation/criterion trajectories over time
- bias plots comparing CNS hypotheses
- ranked next-stimulus recommendations

---

## 10. Success Criteria
The app is successful if it can:
- recover stable peripheral structure under adaptation
- show that different stimuli dissociate CNS hypotheses
- demonstrate that information-optimal designs converge faster than naive sampling
- produce publishable model-comparison results about **how the CNS integrates artificial nerve stimulation**


## Design Motivation from Prior Work
- Prior work shows that reproducing natural sensation requires:
  - selective recruitment of distinct neural subpopulations
  - time-varying stimulation patterns
  - simultaneous control of neuron type, location, and timing
- Static or single-parameter encoders (e.g. sinusoidal, force-based)
  are insufficient for reproducing neural population codes
