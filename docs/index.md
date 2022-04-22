# PsychoAnalyze

Psychophysics analysis in Python.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psychoanalyze) ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

## Installation

```console
$ pip install psychoanalyze
```

## Usage 

```python
>>> import psychoanalyze as pa
>>> trials_df = pa.fake()
>>> curve_df = pa.curve(trials_df)
