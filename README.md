# PsychoAnalyze

Interactive data simulation and analysis for psychophysics.

[![PyPI - Status](https://img.shields.io/pypi/status/psychoanalyze)](https://pypi.org/project/psychoanalyze/)
[![PyPI - Version](https://img.shields.io/pypi/v/psychoanalyze)](https://pypi.org/project/psychoanalyze/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psychoanalyze)](https://pypi.org/project/psychoanalyze/)

[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/psychoanalyze/psychoanalyze/main.svg)](https://results.pre-commit.ci/latest/github/psychoanalyze/psychoanalyze/main)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/docs/user_guide/index.html#user-guide)
[![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?logo=plotly&logoColor=white)](https://psychoanalyze.io)

[![GitHub Discussions](https://img.shields.io/github/discussions/psychoanalyze/psychoanalyze)](https://github.com/orgs/psychoanalyze/discussions)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/psychoanalyze/notebooks/main?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fpsychoanalyze%252Fnotebooks%26urlpath%3Dlab%252Ftree%252Fnotebooks%252Ftutorial.ipynb%26branch%3Dmain)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/psychoanalyze/psychoanalyze)

## Getting Started

| I want to... | You should... |
| ------------ | ------------- |
| ... fit my data to the psychometric function |  visit the [dashboard](https://psychoanalzye.io) and click on the upload box |
| ... incorporate `psychoanalyze` utilities into my Python scripts |  follow the [Installation](#installation) steps below. |
| ... see how `psychoanalyze` is used in a real-world example |  check out the [tutorial notebook](repository) |
| ... see what CLI options are available |  run `psychoanalyze --help` in your terminal|

---

### Installation

PsychoAnalyze is available on PyPI and conda-forge!

Install the usual way in an isolated environment[^1]:

```console
$ pip install psychoanalyze
```

```console
$ conda install -c conda-forge psychoanalyze
```

[^1]: I humbly suggest [hatch](https://hatch.pypa.io/latest/why/) as a modern alternative to *pip* and *poetry* or [mamba/micromamba](https://mamba.readthedocs.io/en/latest/index.html) if you need to use a conda environment. Virtual environment activation steps are left out for broad compatibility, but if you are new to Python, simply run `python -m venv .venv` to install your packages in the project root under the `.venv/` directory.

## Documentation
View the full documentation at [https://docs.psychoanalyze.io](https://docs.psychoanalyze.io).

## Dashboard
See what `psychoanalyze` can do by [viewing our dashboard](https://psychoanalyze.io/).

## Install with Python
```console
$ pip install psychoanalyze
```

### View CLI options
```console
$ psychoanalyze --help
```

## Developers
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/psychoanalyze/psychoanalyze?quickstart=1)

## Notebooks

Example notebooks are hosted in a separate GitHub repository: [psychoanalyze/notebooks](https://github.com/psychoanalyze/notebooks).

### Binder

A fully executable notebook environment is available on Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/psychoanalyze/notebooks/main?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fpsychoanalyze%252Fnotebooks%26urlpath%3Dlab%252Ftree%252Fnotebooks%252Ftutorial.ipynb%26branch%3Dmain)

### JupyterHub on `psychoanalyze.io`

*GitHub login required*

We also host our own JupyterHub instance on the `nb.psychoanalyze.io` domain. If you'd like to try it out, log in via GitHub with [this link](https://nb.psychoanalyze.io/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fpsychoanalyze%2Fnotebooks&urlpath=lab%2Ftree%2Fnotebooks%2Ftutorial.ipynb&branch=main) to spin up your own server.  Your GitHub username will be visible to the maintainers of the project.

### Static

Static HTML copies of notebooks are available by navigating to the `.ipynb` file on GitHub, e.g. [tutorial.ipynb](https://github.com/psychoanalyze/notebooks/blob/main/tutorial.ipynb)

## Deployment

If you'd like to spin up your own instance of the dashboard on the web, you may  use the following button for a Heroku setup:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/heroku/node-js-getting-started)
