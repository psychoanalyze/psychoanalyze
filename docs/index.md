# Getting Started

## Overview

**PsychoAnalyze** was developed to support research for the [Moran Lab](https://moranlab.wustl.edu/) at Washington University in St. Louis. It is a multi-purpose data platform to assist researchers analyzing data from psychophysical experiments.

!!! question "New to psychophysics?"

    *[Psychophysics](https://en.wikipedia.org/wiki/Psychophysics)* is a branch of study within behavioral psychology and neuroscience that provides an experimental and analytical framework for the broad purpose of quantifying the relationship between physical stimuli and perceptual experience. For an excellent review of the history and impact of psychophysics, check out the following review published in *Neuroscience by J.C.A. Read: *[The place of human psychophysics in modern neuroscience](https://www-sciencedirect-com.libproxy.wustl.edu/science/article/pii/S0306452214004369).

## Dashboard
For a high-level view of what you can do with PsychoAnalyze, try out the interactive dashboard at [https://psychoanalyze.io](https://psychoanalyze.io).

For guidance, check out our brief [dashboard guide](dashboard.md), or just start clicking around to see what happens!

Try:

- Simulating data by adjusting model/simulation parameters.
- Downloading results in various file formats:
    - Tabular data: `.csv`, `.parquet`, `.json`, `.duckdb`
    - Figures: `.png`, `.svg`, `.pdf`

- Uploading your own dataset or our [tutorial dataset](/notebooks/tutorial_trials.csv) according to the specified schema and observe/download the model fits.

## Notebook Tutorial
For a more hands-on experience with PsychoAnalyze, enjoy our [notebook tutorial](notebooks/tutorial.ipynb). Consider submitting a notebook of your own to our gallery!

## Python Package

For custom applications, you can use `psychoanalyze` as a Python package (available on [PyPI](https://pypi.org/project/psychoanalyze/)) to develop your own analysis scripts or apps. You'll want to check out our [Python API documentation](api.md) and our [test documentation](tests.md).

### Install in a Python environment

=== "Poetry"

    ```console
    poetry add psychoanalyze
    ```

=== "Pip"

    ```console
    pip install psychoanalyze
    ```


## Want to contribute to PsychoAnalyze?

Check out our [contributing guide](CONTRIBUTING.md) and see what's going on in 💡[Discussions](https://github.com/)!
