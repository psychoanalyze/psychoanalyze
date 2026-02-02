
"""Analysis modules for psychophysical data.

This package contains analysis tools for psychophysical experiments:
- sdt: Signal Detection Theory metrics and ROC analysis
- bayes: Bayesian analysis tools
- ecdf: Empirical cumulative distribution functions
- weber: Weber fraction analysis
- strength_duration: Strength-duration analysis
"""

from psychoanalyze.analysis import sdt

__all__ = ["sdt"]
