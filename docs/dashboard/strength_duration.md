# Strength-Duration Analysis

## Overview

The **Strength-Duration** tab in PsychoAnalyze allows you to analyze and visualize the relationship between stimulus amplitude (strength) and pulse width (duration) at detection threshold. This analysis is fundamental in assessing how the nervous system integrates sensory information over time.

## Theory

Strength-duration curves characterize how the *minimum detectable stimulus amplitude* varies as a function of stimulus *time course*. The relationship follows the **Strength-Duration curve**:

$$A \cdot t = C$$

where:
- $A$ = stimulus amplitude (strength)
- $t$ = stimulus duration
- $C$ = chronaxie (a constant reflecting neural time constant)

This relationship demonstrates **temporal integration**: longer duration stimuli require less amplitude to reach detection threshold.

## Data Format

Upload a CSV or Parquet file with the following required columns:

| Column              | Type    | Description                                                      |
| ------------------- | ------- | ---------------------------------------------------------------- |
| **Subject**         | string  | Subject identifier (optional, default: NONE)                     |
| **Block**           | integer | Experimental block number                                        |
| **Dimension**       | string  | Either "Amp" or "Width" indicating which parameter was modulated |
| **Fixed Magnitude** | float   | The fixed stimulus value (amplitude or width)                    |
| **Threshold**       | float   | The detected threshold at this fixed value                       |

### Example Data Structure

```csv
Subject,Block,Dimension,Fixed Magnitude,Threshold
A,0,Amp,10.0,5.2
A,0,Amp,20.0,3.1
A,0,Amp,30.0,2.1
A,0,Width,100,50.0
A,0,Width,200,35.0
A,0,Width,300,25.0
```

## Data Modulation Modes

### Amplitude-Modulated (Dim = "Amp")
- **X-axis**: Fixed Pulse Width (μs)
- **Y-axis**: Threshold Amplitude (μA)
- Shows how amplitude threshold decreases as pulse width increases

### Width-Modulated (Dim = "Width")
- **X-axis**: Fixed Amplitude (μA)
- **Y-axis**: Threshold Pulse Width (μs)
- Shows how duration threshold decreases as amplitude increases

## Usage

1. **Navigate to Strength-Duration Tab**: Click the "Strength-Duration" tab in the application
2. **Upload Data**: Click the upload area and select your CSV/Parquet file
3. **Visualize**: The dashboard automatically generates plots for each dimension in your data

## Interpretation

### Strength-Duration Characteristics

**Well-behaved curves** exhibit:
- Monotonic relationship (one always increases while the other decreases)
- Smooth progression across stimulus parameters
- Consistency across blocks/sessions

**Unusual patterns** may indicate:
- Fatigue or habituation effects within a block
- Changes in attention or alertness
- Measurement artifacts or equipment issues

### Clinical Applications

Strength-duration curves are particularly useful for:
- **Electrical stimulation**: Characterizing optimal pulse widths for neural interfaces
- **Psychophysical studies**: Understanding temporal integration windows
- **Sensory substitution**: Designing stimulation parameters for perceptual devices

## Analysis Functions

The visualization uses the following functions from `psychoanalyze.analysis.strength_duration`:

- **`from_blocks(blocks, dim)`**: Transform block data into strength-duration format
  - Input: DataFrame with columns [Subject, Block, Dimension, Fixed Magnitude, Threshold]
  - Output: DataFrame with properly labeled axes for plotting

- **`plot(blocks, dim, x_data, y_data)`**: Create scatter plot visualization
  - Automatically applies appropriate axis labels based on modulation dimension
  - Uses the PsychoAnalyze standard Plotly template

## Advanced Features

### Multiple Dimensions
If your data contains both "Amp" and "Width" modulation conditions, separate plots are automatically generated for each.

### Subject Comparison
Upload data from multiple subjects to compare strength-duration characteristics across individuals.

### Error Analysis
Include additional columns for error metrics (standard deviations, confidence intervals) to show variability at each point.

## Troubleshooting

### "No dimensions found in data"
- Check that your data has a "Dimension" column
- Verify values are exactly "Amp" or "Width" (case-sensitive)

### Missing plots
- Verify all required columns are present
- Check data types: Fixed Magnitude and Threshold should be numeric

### Plotting errors
- Check for non-numeric values in Fixed Magnitude or Threshold columns
- Ensure Subject column is present (or will use default)
- Verify Dimension values match expected options

## References

- **Strength-Duration Relationship**: Lapicque, L. (1909). "Definition experimentale de l'excitabilite." Proceedings of the International Society of Electrobiology, 4, 27-35.

- **Temporal Integration in Sensory Systems**: Breitmeyer, B. G., & Ganz, L. (1976). "Implications of maintained and transient channels for theories of visual pattern masking, saccadic suppression, and information processing." Psychological Review, 83(1), 1-36.
