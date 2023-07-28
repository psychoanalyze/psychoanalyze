## Visualization Panel

The Visualization Panel is the central column of the dashboard. It contains the plot of the psychometric function.

!!! abstract On the roadmap:

- Figure-specific controls such as:
    - Axis label/legend visibility and customization
    - Toggle log axes
    - Toggle error bars & aggregation options (e.g. show count on separate plot, toggle mean vs MAP estimate, etc.)

### Psychometric Function Plot

The psychometric function plot is the central feature of the dashboard. It is a plot of the psychometric function, which is a function that describes the relationship between a stimulus intensity level and the probability of a correct response. The psychometric function is a model of the psychophysical process that underlies the data collected in a psychophysical experiment.

The psychometric function plot is generated using the [Plotly](https://plotly.com/python/) Python library. It is an interactive plot that allows the user to zoom in and out, pan, and hover over data points to see their values. Click a legend item to toggle the visibility of the corresponding data series, or double-click a legend item to isolate the trace.
