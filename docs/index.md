# Getting Started

## Introduction

**PsychoAnalyze** was developed to support research in the [Moran Lab](https://moranlab.wustl.edu/) at Washington University in St. Louis. It is a multi-purpose data platform to assist researchers analyzing data from psychophysical experiments, providing prepackaged libraries for helpful data transformation methods, model-fitting routines, and data visualization features specific to psychophysics research, and behavioral psychology/neuroscience in general.

!!! question "New to psychophysics?"

    *[Psychophysics](https://en.wikipedia.org/wiki/Psychophysics)* is a branch of study within behavioral psychology and neuroscience that provides an experimental and analytical framework for the broad purpose of quantifying and modeling the relationship between physical stimuli and perceptual experience. For an excellent review of the history and impact of psychophysics, check out the following review published in *Neuroscience by J.C.A. Read: *[The place of human psychophysics in modern neuroscience](https://doi.org/10.1016/j.visres.2016.02.002).


!!! abstract "About the *alpha* release and our roadmap:"

    *Psychoanalyze* is currently in an [*alpha* release phase](https://en.wikipedia.org/wiki/Software_release_life_cycle#Alpha). It is not feature-complete and makes no guarantees to be bug-free. Visit our [roadmap]() to see our plans for upcoming features. In the meantime, relevant sections of this documentation will contain notes on planned features. Pre-alpha development focused on high-level infrastructure for the project with modularity in mind. *Beta* release will be considered after the accomodation of a much wider variety of experimental formats, analytical methods, and visualization options. Users should expect fast iteration for approved features, especially features requested by the community. Help us accomodate your use case by proposing a feature on GitHub as an [Issue](https://github.com/psychoanalyze/psychoanalyze/issues/new?assignees=&labels=enhancement&projects=&template=feature-request.md&title=%5BNEW%5D) or [Discussion](https://github.com/orgs/psychoanalyze/discussions/categories/ideas).

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

## Python Installation

For custom applications, we provide the `psychoanalyze` Python package (available on [PyPI](https://pypi.org/project/psychoanalyze/)) to use in your own scripts or applications.

To install `psychoanalyze` in a Python virtual environment, run the installation command in your terminal:


=== "Pip"

    ```console
    $ pip install psychoanalyze
    ```
=== "Poetry"

    ```console
    $ poetry add psychoanalyze
    ```

To get started using `psychoanalyze` from the command line, execute the `--help` command in your Python virtual environment:

```console
$ psychoanalyze --help
```

To learn how to use `psychoanalyze` to perform analysis in your own Python scripts and and apps, check out our [notebook examples](notebooks) and our [API reference](api).

## Developers

Want to contribute to PsychoAnalyze's code base, or simply get a local instance of Dash or Jupyter running?

Check out our [contributing guide](CONTRIBUTING.md), or see what's going on in [Discussions](https://github.com/)!💡
