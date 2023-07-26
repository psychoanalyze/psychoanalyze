# Dashboard

The PsychoAnalyze dashboard is featured on the home page of our website:

[https://psychoanalyze.io](https://psychoanalyze.io)

??? abstract "About the *alpha* release and our roadmap:"

    These docs have been written for the *alpha* release of PsychoAnalyze. Visit our [roadmap]() to see how we plan to expand the use cases of our dashboard in upcoming releases. In the meantime, relevant sections will contain notes on planned features. The *alpha* released focused on high-level infrastructure for the project. The next major release will focus on accomodating a wide variety of experimental formats, analytical methods, and visualization options. Help us accomodate your use case by proposing a feature on GitHub as an [Issue](https://github.com/psychoanalyze/psychoanalyze/issues/new?assignees=&labels=enhancement&projects=&template=feature-request.md&title=%5BNEW%5D) or [Discussion](https://github.com/orgs/psychoanalyze/discussions/categories/ideas).

## Introduction

Our dashboard is a *[Dash](https://dash.plotly.com/)* application. *Dash* is a Python framework for building interactive data dashboards that run in the browser.

While Python developers may be interested in examining or contributing to the code that powers the dashboard, use of the dashboard on our site requires no coding knowledge and aims to be useful to people of all backgrounds.

The dashboard is currently designed to be viewed on a full-sized laptop or desktop monitor and consists of three main panels, one for each column in the interface:

- [Input panel](#input-panel)
- [Visualization panel](#visualization-panel)
- [Output Panel](#output-panel)

!!! abstract "On our roadmap:"

    - CSS support for mobile devices and tablets
    - Support for customizing the dashboard layout
    - Support for customizing the dashboard theme
    - Support for Streamlit

### Input Panel

The Input Panel provides the user to determine the data processed by the dashboard, either via upload or selection of model parameters and experimental conditions.

#### Upload data

The first component in the input panel column allows anyone to upload a dataset to be processed by the dashboard. The dataset must be a table either in `.csv` or `.parquet` format, and for now is restricted to be in the form of a very simple schema as follows:

| Column Name | Description | DataType |
| ----------- | ----------- | -------- |
| `Block` | A number representing an ID for a consecutive "block" of trials determined by the researcher. | `int` |
| `Intensity` | A number representing the intensity of the stimulus presented in a trial. | `float` |
| `Result` | The binary outcome of the trial, encoded as a 0 for false and a 1 for true. | `int` |

!!! abstract "On our roadmap:"

    - Support for multiple subjects
    - Support for multi-electrode stimulus arrays
    - Support for longitudinal studies
    - Support for different sensory domains, such as audition and vision.

#### Simulate data

By default, the dashboard displays the results from a simulation of a hypothetical yes-no experiment. A sequence of randomly-sampled trial outcomes are generated, processed, fit the the psychometric function, and visualized, with assistance from PsychoAnalyze's [API functions](api). The simulation estimates the psychometric function's *location* and *scale* parameters according to the chosen [link function](#link-function) $F(x)$, which is the *logistic equation* by default.:

$$
\psi(x) = F(x) = \frac{1}{1 + e^{-\frac{x - \mu}{\sigma}}}
$$

- $\mu$ is the *location* parameter, which represents the psychophysical "threshold".
- $\sigma$ is the *scale* parameter, which represents the slope (*i.e.*, sensitivity) of the psychometric curve near the threshold.

##### Link Function

- In an upcoming release, PsychoAnalyze will support a variety of link functions. For now, the only supported link function is the [logit function](https://en.wikipedia.org/wiki/Logit). You can toggle the visibility of the equation for the logit function by clicking the `Show/Hide` button.

##### Model Parameters

You may adjust the parameters $\mu$ and $\sigma$ for model simulations using the sliders and input boxes in the panel. The simulation is completely regenerated in the browser's memory each time any parameter in the Input Panel is adjusted.

!!! abstract "On our roadmap:"

    - Support for other link functions, beginning with the probit function.
    - Support for other model parameters, such as guess rate, lapse rate, and the *beta* parameter for the [beta-binomial approach](https://doi.org/10.1016/j.visres.2016.02.002).

##### Stimulus

You may adjust the *n levels* parameter to change the number of stimulus intensity levels representing the trial conditions of a [method-of-constant-stimuli](https://en.wikipedia.org/wiki/Psychophysics#Method_of_constant_stimuli) experiment. In the plot, this is represented by the number of dots across the x-axis.

!!! abstract "On our roadmap:"

    - Support for choices of *n_min* and *n_max* that are decoupled from the choice of model parameters.
    - Support for other sampling methods such as method-of-adjustment, method-of-limits, and modern Bayesian sampling algorithms.

##### Simulation

The simulation generates balanced blocks, with a randomly selected stimulus intensity level for each trial. Thus, each block will have exactly *n* trials per block, but the number of trials at each stimulus intensity level *x* will be randomly distributed. The number of blocks is determined by the *n blocks* parameter. Model fits for each block are calculated, but only but only blocks selected in the data table in the Output column in the right-hand side are visible.

!!! abstract "On our roadmap:"

    - Support for unbalanced blocks.
    - Simulation animations
    - Bayesian inferencing methods via PyMC
    - Simulations for model comparisons
