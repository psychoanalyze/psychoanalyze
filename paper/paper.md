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

*PsychoAnalyze* provides data manipulation and visualization tools that accomodate more complex experimental setups than the standard psychophysical analysis software performs today, especially experiments performed over many trial blocks, under a wider variety of experimental conditions.

In addition to a Python package and a command-line tool, *PsychoAnalyze* offers a web-hosted dashboard demonstrating the capabilities of the package. On its own, the dashboard provides researchers with a no-code interface to fit their data to a psychometric function and visualize the results in an interactive figure.

Because Python has rapidly gained popularity among both the scientific and data science communities, a Python package that properly utilizes and integrates the wealth of developer tools and data tools available in the Python ecosystem can provide researchers with proper context for their experimental design, inform ongoing decisions throughout the experiment, and an extensible project structure. Researchers can spend less time wrestling with custom analysis scripts and more time thinking about their data and their models.

For example, psychoanalyze provides methods to:

- Aggregate trial data to an appropriate format (*e.g.*, grouped by intensity level of the stimulus) for model-fitting procedures.

- Generate simulation data according to common psychophysical experimental procedures.

- Export data to a variety of formats such as CSV, Parquet, and DuckDB.

- Transform model parameters from one parameterization to another (*e.g.*, location/scale form to intercept/slope form, or linear form to z-scored form)

$$
\psi(x) = \frac{1}{1 + e^{\alpha + \beta x}} -> \frac{1}{1 + e^{-\frac{(x - \mu)}{\sigma}}}
$$

The *Alpha* release of PsychoAnalyze packaged with this publication demonstrates Various "plug-in" modules may be developed that utilize these libraries and their I/O file formats to provide a more streamlined workflow for data analysis.

# Citations

There are several existing software packages that provide tools for psychophysical analysis.

- [PsychoPy](https://www.psychopy.org/) [@peirce_psychopy2_2019] is a Python package that provides a complete suite of tools for designing and running psychophysical experiments on a personal computer device.

- [PsychToolbox](http://psychtoolbox.org/citations) [@brainard_psychophysics_1997] is a MATLAB package that similarly provides routine for stimulus presentation and data collection.

- [Palamedes](http://www.palamedestoolbox.org/) [@prins_applying_2018] is a MATLAB toolbox that provides an advanced set of curve-fitting procedures, including procedures that use subject-level data to use hierarchical Bayesian methods for more accurate estimates.

- [psignifit](https://github.com/wichmann-lab/psignifit/wiki) [@schutt_painfree_2016] Is primarily developed in MATLAB, but ported to Python. It primarily provides methods for fitting the psychometric function using Bayesian methods.

- [BayesFit](http://doi.org/10.5334/jors.202) [@slugocki_bayesfit:_2019] is a Python-first model-fitting library, but is no longer being actively being maintained.


# Citations


# Acknowledgements


# References
