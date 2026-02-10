# Dashboard

The PsychoAnalyze dashboard is linked to via the :material-chart-bell-curve-cumulative: icon in the navigation bar and is is featured on the home page of our website:

[https://psychoanalyze.io](https://psychoanalyze.io)

## Introduction

Our dashboard is a *[marimo](https://marimo.io/)* notebook (`app.py` at the project root). marimo is a reactive Python notebook that runs in the browser, with Bayesian fit results cached locally on disk to speed repeated runs. The dashboard now runs a single hierarchical fit across Subject-Block pairs, with advanced sampling settings available in the input panel.

While Python developers may be interested in examining or contributing to the code that powers the dashboard, use of the dashboard on our site requires no coding knowledge and aims to be useful to people of all backgrounds.

The dashboard is intended to be viewed on a full-sized laptop or desktop monitor and consists of three main panels (input, plot, and output):

- [Input Panel](input.md)
- [Visualization Panel](viz.md)
- [Output Panel](output.md)

## Analysis Types

The dashboard supports multiple types of psychophysical analyses:

### Primary Analyses

**Psychometric Function Fitting** (Simulation, Batch, Online modes)
- Hierarchical Bayesian fitting of detection thresholds
- Supports multiple blocks, subjects, and modalities
- Real-time visualization with credible bands

### Specialized Analyses

**[Strength-Duration Analysis](strength_duration.md)**
- Assess temporal integration in sensory systems
- Visualize how stimulus amplitude and duration trade off at threshold
- Test the Strength-Duration relationship for neural stimulation parameters

**[Weber's Law Analysis](weber.md)**
- Quantify stimulus discriminability across intensity ranges
- Test Weber's Law (constant Weber fraction) hypothesis
- Compare discrimination abilities across subjects and stimulus modalities

!!! abstract "On our roadmap:"

    - Responsive styling for mobile devices and tablets
    - Support for customizing the dashboard layout
    - Support for customizing the dashboard theme
    - Streamlit integration
    - Additional analysis types (Temporal Contrast, Concurrent Masking)
