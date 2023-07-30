---
title: 'PsychoAnalyze: Interactive data tools for psychophysics.'
tags:
  - Python
  - psychophysics
  - behavioral psychology
  - neuroscience
authors:
  - name: Tyler C Schlichenmeyer
    orcid: 0000-0003-0608-6119
    corresponding: true
    affiliation: 1
  - name: Daniel W Moran
    affiliation: 1
affiliations:
 - name: Department of Biomedical Engineering, Washington University in St. Louis, USA
   index: 1
date: 29 July 2023
bibliography: paper.bib
---

# Summary

*Psychophysics* is a subdomain of behavioral psychology that provides an experimental and analytical framework to model and quantify the physical relationship between sensory stimuli and the sensations and perceptions they produce.

At the core of the psychophysical model is the *psychometric function*, a function that maps graded dimensions of the input stimulus to some experimental measure of the subject's induced response. The psychometric function is a model of the neural sensory systems and mechanisms that underlie the data collected in a psychophysical experiment. The estimation and categorization of these parameters in various experimental conditions is at the center of most avenues of psychophysical analysis.

# Statement of need

## Existing software

There are several existing software packages that provide tools for psychophysical analysis.

- [PsychoPy](https://www.psychopy.org/) [@peirce_psychopy2_2019] is a Python package that provides a complete suite of tools for designing and running psychophysical experiments on a personal computer device.

- [PsychToolbox] is a MATLAB package that similarly provides routine for stimulus presentation and data collection.

- [Palamedes](http://www.palamedestoolbox.org/) is a MATLAB toolbox that provides an advanced set of curve-fitting procedures, including procedures that use subject-level data to use hierarchical Bayesian methods for more accurate estimates.

- [psignifit] Is primarily developed in MATLAB, but ported to Python. It primarily provides methods for fitting the psychometric function using Bayesian methods.

- [BayesFit] is a Python-first model-fitting library, but is no longer being actively being maintained.

As described, these packages mostly focus on stimulus presentation software or model-fitting methods. *PsychoAnalyze* seeks to provide additional data manipulation and visualization tools for the ongoing experiment, especially experiments performed with a large number of trial blocks and a variety of experimental conditions. Various "plug-in" modules may be developed that utilize these libraries and their I/O file formats to provide a more streamlined workflow for data analysis.

While *PsychoAnalyze* may utilize these tools or its own procedures to estimate the parameters of the psychophysical model, the main value of the package lies in the data transformation and data visualization methods that may greatly streamline researchers' ability to explore and assess their data without needing to build custom analysis scripts of their own.

For example, psychoanalyze provides methods to:

- Aggregate trial data to an appropriate format (*e.g.*, grouped by intensity level of the stimulus) for model-fitting procedures.

- Generate simulation data according to common psychophysical experimental procedures.

- Export data to a variety of formats such as CSV, Parquet, and DuckDB.

- Transform model parameters from one parameterization to another (*e.g.*, location/scale form or intercept/slope form)



# Citations


# Acknowledgements


# References
