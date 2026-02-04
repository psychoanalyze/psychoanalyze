# Weber's Law Analysis

## Overview

The **Weber's Law** tab in PsychoAnalyze allows you to analyze and visualize how sensory *discriminability* relates to baseline stimulus *intensity*. This analysis tests one of the most fundamental principles in psychophysics: the **Weber-Fechner Law**.

## Theory

**Weber's Law** states that the smallest detectable difference in stimulus intensity is proportional to the baseline (reference) intensity:

$$\Delta I = k \cdot I$$

or equivalently:

$$\frac{\Delta I}{I} = k$$

where:
- $I$ = reference (baseline) stimulus intensity
- $\Delta I$ = difference threshold (just-noticeable difference, JND)
- $k$ = Weber fraction (a constant for a given sensory modality)

This relationship reveals that **sensory perception is logarithmic** rather than linear: a 10% increase in stimulus intensity is perceived similarly regardless of the baseline intensity.

## Data Format

Upload a CSV file with the following required columns:

| Column                        | Type   | Description                                  |
| ----------------------------- | ------ | -------------------------------------------- |
| **Subject**                   | string | Subject identifier                           |
| **Dimension**                 | string | Stimulus dimension (e.g., "Amp", "Width")    |
| **Reference Charge (nC)**     | float  | Reference stimulus intensity                 |
| **Difference Threshold (nC)** | float  | Detected difference threshold (JND)          |
| **Date**                      | string | Date of observation (ISO format: YYYY-MM-DD) |
| **location_CI_5**             | float  | Lower confidence interval (5th percentile)   |
| **location_CI_95**            | float  | Upper confidence interval (95th percentile)  |
| **Fixed_Param_Value**         | float  | Fixed parameter value during testing         |
| **Threshold_Charge_nC**       | float  | Absolute threshold in nanoCharges            |

### Example Data Structure

```csv
Subject,Dimension,Reference Charge (nC),Difference Threshold (nC),Date,location_CI_5,location_CI_95,Fixed_Param_Value,Threshold_Charge_nC
U,Amp,10.0,2.5,2023-01-15,0.8,1.2,50,1.4
U,Amp,20.0,4.8,2023-01-15,1.6,2.4,50,2.8
U,Amp,50.0,11.2,2023-01-15,3.8,5.6,50,7.0
Y,Amp,10.0,1.8,2023-01-15,0.6,0.9,50,1.0
Y,Amp,20.0,3.5,2023-01-15,1.2,1.8,50,2.1
Y,Amp,50.0,8.4,2023-01-15,2.8,4.2,50,5.2
```

## Usage

1. **Navigate to Weber's Law Tab**: Click the "Weber's Law" tab in the application
2. **Upload Data**: Click the upload area and select your CSV file in the weber_curves.csv format
3. **Visualize**: The dashboard generates an interactive scatter plot with trendlines

## Visualization Features

### Main Plot Components

1. **Scatter points**: Individual observations of (Reference Intensity, Difference Threshold)
2. **Color coding**: Different subjects distinguished by color
3. **Symbol coding**: Different stimulus dimensions shown as different symbol shapes
4. **Trendline**: Ordinary Least Squares (OLS) regression line showing the fitted relationship
5. **Error bars**: Confidence intervals around each measurement (5th-95th percentiles)
6. **Hover data**: Reference charge, difference threshold, and measurement date

### Interpretation

**Linear relationship** between Reference Charge and Difference Threshold indicates:
- ✓ Weber's Law holds across the tested intensity range
- ✓ Consistent neural encoding of stimulus differences
- ✓ Sensory system maintains constant discriminability at all stimulus levels

**Non-linear patterns** may indicate:
- Deviations from Weber's Law at extreme intensities
- Changes in discrimination ability with stimulus modality
- Effects of attention, fatigue, or learning

### Weber Fraction Calculation

The slope of the fitted line represents the **Weber fraction** ($k$):

$$k = \frac{\text{slope}}{100}$$

- **Typical Weber fractions** (examples):
  - Brightness: 0.02 (excellent discrimination)
  - Loudness: 0.05 (good discrimination)
  - Weight: 0.02 (good discrimination)

Smaller Weber fractions indicate finer discrimination ability.

## Data Loading and Processing

The `weber.load()` function preprocesses raw weber_curves.csv files:

1. **Datetime conversion**: Converts Date string to datetime objects
2. **Type casting**: Ensures numeric columns are float64
3. **Error calculation**: Computes error bars from CI percentiles:
   - `err+` = upper CI - measurement
   - `err-` = measurement - lower CI

### Custom Data Preparation

If your data is in a different format, ensure:
1. Numeric columns are properly typed (float, not string)
2. Date column is in ISO format or convertible to datetime
3. Error metrics can be computed from your confidence intervals

Example custom loading:

```python
import polars as pl

weber_data = pl.read_csv("my_weber_data.csv")
weber_data = weber_data.with_columns([
    pl.col("RefCharge").alias("Reference Charge (nC)"),
    pl.col("JND").alias("Difference Threshold (nC)"),
])
# Then visualize with weber.plot(weber_data)
```

## Analysis Functions

The visualization uses the following functions from `psychoanalyze.analysis.weber`:

- **`plot(data, trendline="ols", error_y=None)`**: Create interactive scatter plot
  - Input: DataFrame with Weber analysis columns
  - Output: Plotly figure with scatter points, trendline, and optional error bars
  - Trendline options: "ols" for linear regression (default) or None

- **`aggregate(data)`**: Compute summary statistics per subject/dimension/intensity
  - Groups by [Subject, Dimension, Reference Charge]
  - Aggregates: mean difference threshold, count, standard deviation

- **`load(path)`**: Load and preprocess weber_curves.csv format
  - Handles datetime conversion and error bar calculation
  - Returns properly formatted DataFrame ready for plotting

## Advanced Features

### Multi-Subject Comparison
Upload data from multiple subjects to compare Weber fractions across individuals:
- Visual discrimination between subjects (color-coded points)
- Different trendlines may emerge if discriminability varies

### Dimension Effects
If data includes multiple stimulus dimensions, each is represented with a different symbol:
- Compare Weber's Law across modalities (e.g., Amplitude vs. Width)
- Assess whether sensory encoding follows the same principle for different stimulus dimensions

### Longitudinal Analysis
If data spans multiple dates, visualize changes in discriminability over time:
- Track learning effects or adaptation
- Identify fatigue or performance changes

## Troubleshooting

### "Error visualizing Weber data"
- Verify CSV format matches weber_curves.csv structure
- Check that all required columns are present
- Ensure numeric columns contain valid numbers (not text)

### Missing error bars
- Check that location_CI_5 and location_CI_95 columns are present
- Verify these columns contain numeric values
- Error bars are only shown if error_y parameter is set

### No trendline visible
- The trendline is added by default; if not visible, check plot axes scaling
- Verify data has adequate range for a visible trend
- Consider zooming in on the plot to see the line better

## Biological Significance

Weber's Law has profound implications for understanding sensory systems:

### Logarithmic Encoding
The brain encodes stimulus intensity logarithmically, not linearly. This means:
- A doubling of stimulus intensity produces a constant perceived change
- The nervous system uses a "proportional coding" scheme
- Limited neural resources are distributed efficiently across the stimulus range

### Evolutionary Advantage
This logarithmic encoding provides:
- **Efficient range compression**: Wide dynamic range squeezed into limited neural code
- **Adaptive sensitivity**: Fine discrimination where needed, coarse at extremes
- **Metabolic efficiency**: Resources allocated proportionally to discriminability needs

### Exceptions and Deviations
- **Near threshold**: Loss of contrast sensitivity at very low intensities
- **Saturation**: Compressed discrimination at very high intensities
- **Cross-modal differences**: Different sensory systems have different Weber fractions

## References

- **Weber, E. H.** (1834). *De tactu: A treatise on the sense of touch*. Leipzig.

- **Fechner, G. T.** (1860). *Elemente der Psychophysik*. Breitkopf und Härtel. [Translated as *Elements of Psychophysics*, 1966]

- **Stevens, S. S.** (1957). "On the psychophysical law." *Psychological Review*, 64(3), 153-181.

- **Gescheider, G. A.** (1997). *Psychophysics: The fundamentals*. (3rd ed.). Lawrence Erlbaum Associates.

## See Also

- [Strength-Duration Analysis](strength_duration.md) - Temporal integration in sensory systems
- [ECDF Analysis](../ecdf.md) - Empirical cumulative distribution functions for threshold estimation
- [Hierarchical Model](../hierarchical_model.md) - Bayesian fitting of psychometric functions
