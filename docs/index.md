# Getting Started

## Introduction

**PsychoAnalyze** was developed to support research for the [Moran Lab](https://moranlab.wustl.edu/) at Washington University in St. Louis. It is a multi-purpose data platform to assist researchers analyzing data from psychophysical experiments, providing prepackaged libraries for helpful data transformation methods, model-fitting routines, and data visualization features specific to this research domain.

!!! question "New to psychophysics?"

    *[Psychophysics](https://en.wikipedia.org/wiki/Psychophysics)* is a branch of study within behavioral psychology and neuroscience that provides an experimental and analytical framework for the broad purpose of quantifying and modeling the relationship between physical stimuli and perceptual experience. For an excellent review of the history and impact of psychophysics, check out the following review published in *Neuroscience by J.C.A. Read: *[The place of human psychophysics in modern neuroscience](https://doi.org/10.1016/j.visres.2016.02.002).

## Dashboard

For a high-level view of what you can do with PsychoAnalyze, try out the interactive dashboard at [https://psychoanalyze.io](https://psychoanalyze.io).

For guidance, check out our brief [dashboard guide](dashboard.md), or just start clicking around to see what happens!

Try...

- Simulating data by adjusting model simulation parameters.
- Downloading results in various file formats:
    - Tabular data: `.csv`, `.parquet`, `.json`, `.duckdb`
    - Figures: `.png`, `.svg`, `.pdf`

- Uploading your own dataset or our [tutorial dataset](/notebooks/tutorial_trials.csv) according to the specified schema and observe/download the model fits.

## Notebook Tutorial
For a more hands-on experience with PsychoAnalyze, enjoy our [notebook tutorial](notebooks/tutorial.ipynb). Consider submitting a notebook of your own to our gallery!

## Python Package

For custom applications, you can use `psychoanalyze` as a Python package (available on [PyPI](https://pypi.org/project/psychoanalyze/)) to develop your own analysis scripts or apps.

To install `psychoanalyze` in a Python virtual environment:

=== "Poetry"

    ```console
    poetry add psychoanalyze
    ```

=== "Pip"

    ```console
    pip install psychoanalyze
    ```

To get started using `psychoanalyze` from the command line, execute:

```console
psychoanalyze --help
```

in your virtual environment for an overview of the available commands.

For a tutorial on using `psychoanalyze` to perform analysis in your own Python scripts and and apps, check out our section on [notebooks](notebooks).

## Developers

Want to contribute to PsychoAnalyze's code base, or simply get a local instance of Dash or Jupyter running?

Check out our [contributing guide](CONTRIBUTING.md), or see what's going on in [Discussions](https://github.com/)!💡
