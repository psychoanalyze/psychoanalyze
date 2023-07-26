# Dashboard

## Introduction

Our dashboard is featured on our [home page](https://psychoanalyze.io) and is powered by [Dash](https://dash.plotly.com/), a Python framework for building interactive data dashboards using the Flask web framework.

While power users may be interested in examining or contributing to the code that powers the dashboard, use of the dashboard on our site requires no coding knowledge to use and aims to be of interest to people of all backgrounds.

The dashboard is currently designed to be viewed on a full-sized laptop or desktop monitor and consists of 3 main components, 1 for each column in the interface:

### Input panel

#### Upload data

The first component in the input panel column allows anyone to upload a dataset to be processed by the dashboard. The dataset must be a table either in `.csv` or `.parquet` format, and for now is restricted to be in the form of a very simple schema as follows:

| Column Name | Description | DataType |
| ----------- | ----------- | -------- |
| `Block` | A number representing an ID for a consecutive "block" of trials determined by the researcher. | `int` |
| `Intensity` | A number representing the intensity of the stimulus presented in a trial. | `float` |
| `Result` | The binary outcome of the trial, encoded as a 0 for false and a 1 for true. | `int` |

!!! info

    The ability for the dashboard to process more complex schemas is a top priority on our roadmap. For more info or questions, visit the dedicated [topic]() on GitHub Discussions where the community may suggest schemas they would like to see supported.
