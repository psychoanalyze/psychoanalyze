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

*Psychophysics* is a subdomain of behavioral psychology and neuroscience that provides an experimental and analytical framework to model the physical relationship between sensory stimuli and the sensations and perceptions they induce.

At the core of the psychophysical model is the *psychometric function*, a hypothetical function that maps graded dimensions of the input stimulus to some experimental measure of the subject's induced response. Several software packages exist that provide tools for fitting the psychometric function to experimental data, but few provide tools for data manipulation and visualization that accomodate more complex experimental setups that require intricate data flows.

*PsychoAnalyze* aims to make more advanced psychophysical analysis accessible to researchers without extensive software or data engineering background, and to provide an accessible development platform to encourage contributors from all backgrounds to contribute to the project.

# Statement of need

*PsychoAnalyze* provides data manipulation and visualization tools built on modularity and extensibility, aiming to empower researchers to more fully explore and contextualize their data, while minimizing time spent wrestling with custom analysis scripts.

In addition to a Python package and a command-line tool, *PsychoAnalyze* offers a web-hosted dashboard demonstrating the capabilities of the package. On its own, the dashboard provides researchers with a no-code interface to fit their data to a psychometric function and visualize the results in an interactive setting. Further, developers may examine the dashboard code to contextualize the API of the package/library functions.

Because Python has rapidly gained popularity among both the scientific and data science communities, a Python package that properly utilizes and integrates the wealth of developer tools and data tools available in the Python ecosystem can provide researchers and developers with stronger mental models and a tighter feedback loop.

For example, PsychoAnalyze provides convenient methods to:

- Aggregate trial-level data to an appropriate format (*e.g.*, grouped by intensity level of the stimulus) for model-fitting procedures.

- Generate simulation data according to common psychophysical experimental procedures.

- Export results to a variety of formats such as CSV, Parquet, and DuckDB (data) or PNG, SVG, and PDF (figures).

- Transform model parameters between parameterizations, *e.g.* *location $\mu$ / scale $\sigma$* form to *intercept $\beta_0$ / slope $\beta_1$* form:

  $$
  \psi(x) = \frac{1}{1 + e^{-\frac{(x - \mu)}{\sigma}}} \iff \frac{1}{1 + e^{-(\beta_0 + \beta_1 x)}}
  $$

# Roadmap

The release of PsychoAnalyze corresponding to this submission is labeled as an *alpha* (v1.0.0) release, primarily conveying that the software is not feature complete. Software development in the *pre-alpha* phase focused on breadth and extensibility over supporting a wide range of customizable options from the start, although the ability to factor in such options was factored into project architecture. Integration of developer tooling and careful project architecture were priorities, with the intention of enabling rapid iteration of features in the next release phase. Development will likely prioritize "plug-in" modules for the software packages in the following *Citations* section and more advanced features outlined in the project roadmap on GitHub.

*PsychoAnalyze* was developed in support of the research of the authors [@schlichenmeyer_detection_2022]. This research, in addition to feedback and requests from the community, will inform the next iteration of development.

# Citations

There are several existing software packages that provide tools for psychophysical analysis. PsychoAnalyze seeks to bridge the gap in the data pipeline between experimental design software such as *PsychoPy*/*PsychToolbox* and model-fitting software such as *Palamedes*/*psignifit*.

- [PsychoPy](https://www.psychopy.org/) [@peirce_psychopy2_2019] is a Python package that provides a complete suite of tools for designing and running psychophysical experiments on a personal computer device.

- [PsychToolbox](http://psychtoolbox.org/citations) [@brainard_psychophysics_1997] is a MATLAB package that similarly provides routines for stimulus presentation and data collection.

- [Palamedes](http://www.palamedestoolbox.org/) [@prins_applying_2018] is a MATLAB toolbox that provides an advanced set of curve-fitting procedures, including procedures that use subject-level data to use hierarchical Bayesian methods for more accurate estimates.

- [psignifit](https://github.com/wichmann-lab/psignifit/wiki) [@schutt_painfree_2016] Is primarily developed in MATLAB, but ported to Python. It mainly provides methods for fitting the psychometric function using Bayesian methods.

- [BayesFit](http://doi.org/10.5334/jors.202) [@slugocki_bayesfit:_2019] is a Python-first model-fitting library, but is no longer being actively being maintained.


# Acknowledgements

Portions of this work were sponsored by the Defense Advanced Research Projects Agency (DARPA) Biological Technologies Office (BTO) Hand Proprioception and Touch Interfaces (HAPTIX) program under the auspices of Dr Doug Weber through the DARPA Contracts Management Office Cooperative Agreement No. HR0011-15-2-0007.

# References
