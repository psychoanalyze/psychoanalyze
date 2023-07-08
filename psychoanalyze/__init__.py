"""Top-level module of the `psychoanalyze` package.

Most submodules of `psychoanalyze` are organized according to the granularity
of various levels in the hierarchy of the data. These submodules are as follows:

- **Blocks** are perhaps the most analytically significant objects in the hierarchy.
They represent a specific set of experimental conditions and generally correspond
to a single fit of the psychometric function.

- **Points** correspond to the aggregate measures of method-of-constant-stimuli
experiments at each stimulus level measured. For example, a block that samples 8
stimulus intensity levels would have 8 corresponding points.

- **Sessions** represent a single day of experiments performed by a subject. It may
contain several blocks.

- **Subjects** and **trials** are self-explanatory

- The **data** module performs general-purpose data transformation and analysis
functions that do not fit easily into one of the above labels.

`psychoanalyze` also contains other submodules relating to specific lines of
psychophysical analysis.

- **strength_duration** contains functions assessing the relationship
between the amplitude and the time course of the stimulus.

- **weber** contains functions assessing how discriminability of two stimuli
relates to the baseline intensities of the stimuli according to Weber's Law.

- **gescheider** contains various examples of plots and measures included in
George Gescheider's textbook, *Psychophysics: The Fundamentals*.

- **schemas** contains data table schemas of the hierarchical entities described above.

- **plot** contains functions assisting with the plotting of all of the above modules.

"""
