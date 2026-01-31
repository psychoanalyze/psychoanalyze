## Input Panel

The Input Panel provides the user to determine the data processed by the dashboard, either via upload or selection of model parameters and experimental conditions.

### Upload data

The first component in the input panel column allows anyone to upload a dataset to be processed by the dashboard. The dataset must be a table either in `.csv` or `.parquet` format, and for now is restricted to be in the form of a very simple schema as follows:

| Column Name | Description | DataType |
| ----------- | ----------- | -------- |
| `Subject` | Optional subject identifier for multi-subject datasets. | `string` |
| `Block` | A number representing an ID for a consecutive "block" of trials determined by the researcher. | `int` |
| `Intensity` | A number representing the intensity of the stimulus presented in a trial. | `float` |
| `Result` | The binary outcome of the trial, encoded as a 0 for false and a 1 for true. | `int` |

!!! abstract "On our roadmap:"

    - Advanced subject filtering and grouping controls
    - Support for multi-electrode stimulus arrays
    - Support for longitudinal studies
    - Support for different sensory domains, such as audition and vision.

### Simulate data

By default, the dashboard displays the results from a simulation of a hypothetical yes-no experiment. A sequence of randomly-sampled trial outcomes are generated, processed, fit to the psychometric function using PyMC-based Bayesian logistic regression, and visualized, with assistance from PsychoAnalyze's [API functions](../api.md). The simulation estimates the psychometric function's *location* and *scale* parameters according to the chosen [link function](#link-function) $F(x)$, which is the *logistic equation* by default.:

$$
\psi(x) = F(x) = \frac{1}{1 + e^{-\frac{x - \mu}{\sigma}}}
$$

- $\mu$ is the *location* parameter, which represents the psychophysical "threshold".
- $\sigma$ is the *scale* parameter, which represents the slope (*i.e.*, sensitivity) of the psychometric curve near the threshold.

#### Link Function

- In an upcoming release, PsychoAnalyze will support a variety of link functions. For now, the only supported link function is the [logit function](https://en.wikipedia.org/wiki/Logit). You can toggle the visibility of the equation for the logit function using the **Show F(x)** control.

#### Model Parameters

You may adjust the parameters $x_0$, $k$, $\gamma$, and $\lambda$ for model simulations using the sliders and input boxes in the panel. Free/fixed toggles let you lock parameters to preset values while continuing to edit the others. The simulation is regenerated in memory each time any parameter in the Input Panel is adjusted, while Bayesian fit results are cached locally on disk to speed repeated runs.

Cached fit artifacts are stored under `__marimo__/cache/psychoanalyze` in the project directory.

!!! abstract "On our roadmap:"

    - Support for other link functions, beginning with the probit function.
    - Support for additional model parameters, such as the *beta* parameter for the [beta-binomial approach](https://doi.org/10.1016/j.visres.2016.02.002).

#### Stimulus

You may adjust the *n levels* parameter to change the number of stimulus intensity levels representing the trial conditions of a [method-of-constant-stimuli](https://en.wikipedia.org/wiki/Psychophysics#Method_of_constant_stimuli) experiment. In the plot, this is represented by the number of dots across the x-axis.

!!! abstract "On our roadmap:"

    - Support for choices of *n_min* and *n_max* that are decoupled from the choice of model parameters.
    - Support for other sampling methods such as method-of-adjustment, method-of-limits, and modern Bayesian sampling algorithms.

#### Simulation

The simulation generates balanced blocks, with a randomly selected stimulus intensity level for each trial. Thus, each block will have exactly *n* trials per block, but the number of trials at each stimulus intensity level *x* will be randomly distributed. The number of blocks is determined by the *n blocks* parameter. Model fits for each block are calculated, but only but only blocks selected in the data table in the Output column in the right-hand side are visible.

!!! abstract "On our roadmap:"

    - Support for unbalanced blocks.
    - Simulation animations
    - Faster Bayesian inference options for large datasets
    - Simulations for model comparisons
