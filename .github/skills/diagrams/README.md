# PsychoAnalyze D2 Diagrams

This directory contains D2 diagram source files for the PsychoAnalyze project.

## Available Diagrams

### 1. Data Hierarchy (`data-hierarchy.d2`)
**Description**: Illustrates the core data model showing the transformation from individual trials through aggregation layers to final analysis.

**Key Elements**:
- Trials: Individual stimulus presentations (Intensity, Result)
- Points: Aggregated hit rates by intensity
- Blocks: Fitted psychometric curves (threshold, slope)
- Sessions: Longitudinal groupings by time/subject

**View Online**: Copy the contents of `data-hierarchy.d2` to https://play.d2lang.com/

---

### 2. Module Architecture (`module-architecture.d2`)
**Description**: Shows the relationships between key modules in the `src/psychoanalyze/` package.

**Key Elements**:
- Data layer: trials.py, points.py, blocks.py, sessions.py
- Analysis layer: bayes.py, ecdf.py, weber.py, strength_duration.py
- Core utilities: sigmoids.py, plot.py, params.py
- Application: app.py (Marimo dashboard)

**View Online**: Copy the contents of `module-architecture.d2` to https://play.d2lang.com/

---

### 3. Analysis Workflow (`analysis-workflow.d2`)
**Description**: Depicts the complete data processing pipeline from raw input to final results.

**Key Elements**:
- Input stage: CSV/Excel data loading
- Preprocessing: Schema validation and aggregation
- Model fitting: Logistic regression and Bayesian methods
- Analysis: ECDF, Weber, strength-duration analyses
- Visualization: Dashboard and plotly figures
- Output: Thresholds, slopes, statistics

**View Online**: Copy the contents of `analysis-workflow.d2` to https://play.d2lang.com/

---

### 4. Psychometric Function (`psychometric-function.d2`)
**Description**: Visual representation of the psychometric function formula and its computation steps.

**Formula**: `ψ(x) = γ + (1 - γ - λ) × F(x; x₀, k)`

**Key Elements**:
- Parameters: x (stimulus), x₀ (threshold), k (slope), γ (guess rate), λ (lapse rate)
- Link function F: logistic, Weibull, Gumbel, or Quick
- Computation flow: input → link transform → scale → shift → output

**View Online**: Copy the contents of `psychometric-function.d2` to https://play.d2lang.com/

---

## Rendering D2 Diagrams

### Option 1: Online Playground
1. Open https://play.d2lang.com/
2. Copy the contents of any `.d2` file
3. Paste into the editor
4. The diagram renders automatically
5. Export as SVG or PNG

### Option 2: Local CLI
If you have d2 installed:
```bash
# Install d2 (requires Go or use pre-built binary)
# See: https://github.com/terrastruct/d2

# Render a diagram
d2 data-hierarchy.d2 data-hierarchy.svg

# Render with specific theme
d2 --theme=dark data-hierarchy.d2 data-hierarchy-dark.svg

# Render all diagrams
for file in *.d2; do
  d2 "$file" "${file%.d2}.svg"
done
```

### Option 3: VS Code Extension
Install the "D2" extension in VS Code for inline preview and editing support.

## D2 Syntax Basics

D2 uses a simple declarative syntax:

```d2
# Basic shape
MyShape: {
  label: "Display text"
  shape: rectangle  # or oval, cylinder, diamond, hexagon, etc.
  style.fill: "#e8f4f8"
}

# Connection
A -> B: "label on arrow"

# Nested containers
Container: {
  Item1
  Item2
  Item1 -> Item2
}

# Styling
MyShape: {
  style: {
    fill: "#ffffff"
    stroke: "#000000"
    stroke-width: 2
    font-size: 14
  }
}
```

## Customization

All diagrams can be customized by:
- Changing colors (hex codes in `style.fill`)
- Adjusting layout direction (`direction: down|right|left|up`)
- Modifying shapes (`shape: rectangle|oval|cylinder|diamond|hexagon|...`)
- Adding/removing elements
- Changing labels and annotations

## Integration with Documentation

These diagrams can be:
- Rendered to SVG and included in documentation
- Embedded in README files
- Used in presentations and papers
- Version controlled alongside code
- Generated programmatically via GitHub Copilot skill

## Learn More

- [D2 Language Documentation](https://d2lang.com/tour/intro)
- [D2 GitHub Repository](https://github.com/terrastruct/d2)
- [D2 Examples Gallery](https://d2lang.com/gallery)
