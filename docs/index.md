# PsychoAnalyze

Interactive data exploration for psychophysics.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psychoanalyze) ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)


## Installation

=== "Poetry"

    ```console
    poetry add psychoanalyze
    ```

=== "Pip"

    ```console
    pip install psychoanalyze
    ```

## Getting Started

``` py
import psychoanalyze as pa
```

Generate 100 random Bernoulli trials where x (the intensity of the modulated stimulus dimension) is chosen from x=-4 to x=4:

``` py
trials = pa.trial.generate(100,list(range(-4,5)))
trials.T
```

## Dashboard

See what `psychoanalyze` can do by [visiting our dashboard](https://psychoanalyze.herokuapp.com/).


--8<-- "docs/tables/table1.html"

--8<-- "docs/figures/fig1.html"

--8<-- "docs/jupyterlite.html"
