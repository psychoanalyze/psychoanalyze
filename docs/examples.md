# Examples

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/schlich/psychoanalyze/blob/main/docs/notebook.ipynb)

``` py
import psychoanalyze as pa
```

Generate 100 random Bernoulli trials where x (the intensity of the modulated stimulus dimension) is chosen from x=-4 to x=4:

``` py
trials = pa.trial.generate(100,list(range(-4,5)))
trials.T
```

--8<-- "docs/tables/table1.html"

--8<-- "docs/figures/fig1.html"

--8<-- "docs/jupyterlite.html"