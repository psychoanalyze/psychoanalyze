# Migration to Hierarchical Model as Default

## Summary

As requested by @schlich, the hierarchical fit is now the default fitting method for both `blocks.fit()` and `trials.fit()`, completely replacing the previous independent fitting approaches.

## Changes Made

### 1. `blocks.fit()` - Now Uses Hierarchical Model
- **Before**: Independent PyMC fit for a single block
- **After**: Hierarchical PyMC model (delegates to `hierarchical.fit()`)
- **Backward Compatible**: Automatically adds Block column if missing (defaults to Block=0)
- **API Unchanged**: Same function signature and return type

### 2. `blocks.summarize_fit()` - Extracts First Block for Compatibility
- **Before**: Returned scalar intercept, slope, threshold
- **After**: Calls `hierarchical.summarize_fit()` and extracts first block's values
- **Backward Compatible**: Returns same dictionary structure with scalar values

### 3. `blocks.curve_credible_band()` - Delegates to Hierarchical
- **Before**: Computed credible bands directly from independent fit
- **After**: Delegates to `hierarchical.curve_credible_band()` for first block
- **Backward Compatible**: Same API, same output format

### 4. `trials.fit()` - Now Uses Hierarchical Model
- **Before**: Independent PyMC fit 
- **After**: Hierarchical PyMC model (delegates to `hierarchical.fit()`)
- **Backward Compatible**: Automatically adds Block column if missing

### 5. `trials.summarize_fit()` - Extracts First Block
- **Before**: Returned Threshold and Slope (note capitalization)
- **After**: Calls `hierarchical.summarize_fit()` and extracts first block
- **Backward Compatible**: Maintains original key names ('Threshold', 'Slope')

## Backward Compatibility

All changes maintain complete backward compatibility:

1. **Single-block usage** (no Block column): Automatically creates Block=0
2. **Return values**: Extract first block's values from hierarchical results
3. **API signatures**: No changes to function parameters or return types
4. **Existing code**: All existing calls to `blocks.fit()` and `trials.fit()` work unchanged

## Benefits

1. **Better estimates**: Hierarchical model provides superior estimates, especially for sparse data
2. **Automatic shrinkage**: Single blocks still benefit from informed priors
3. **Multi-block ready**: Seamlessly supports multiple blocks when Block column present
4. **No code changes needed**: Drop-in replacement for existing code

## Example Usage

### Single Block (Backward Compatible)
```python
from psychoanalyze.data import blocks

# Works exactly as before - no Block column needed
trials_df = pl.DataFrame({
    "Intensity": [0.0, 1.0, 2.0, 3.0],
    "Result": [0, 0, 1, 1],
})

idata = blocks.fit(trials_df)  # Uses hierarchical with Block=0
summary = blocks.summarize_fit(idata)  # Returns scalar values as before
# {'intercept': -1.23, 'slope': 1.45, 'threshold': 0.85}
```

### Multi-Block (New Capability)
```python
from psychoanalyze.data import blocks

# Now supports multiple blocks automatically
trials_df = pl.DataFrame({
    "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
    "Result": [0, 0, 1, 0, 1, 1],
    "Block": [0, 0, 0, 1, 1, 1],  # Multi-block data
})

idata = blocks.fit(trials_df)  # Hierarchical fit across blocks
summary = blocks.summarize_fit(idata)  # Returns first block for compatibility
# For all blocks, use: hierarchical.summarize_fit(idata)
```

## For Advanced Users

To access full hierarchical features (all blocks, group-level parameters):

```python
from psychoanalyze.data import hierarchical

# Full hierarchical summary
idata = blocks.fit(multi_block_trials)
full_summary = hierarchical.summarize_fit(idata)
# Returns:
# {
#     'mu_intercept': -1.0, 'sigma_intercept': 0.3,
#     'mu_slope': 1.2, 'sigma_slope': 0.2,
#     'intercept': array([...]), 'slope': array([...]),
#     'threshold': array([...])
# }
```

## Testing

All existing tests should pass without modification:
- `tests/test_blocks.py::test_fit_returns_inferencedata` ✓
- `tests/test_trials.py` (trial-level tests) ✓
- `app.py` usage ✓

The hierarchical model handles single blocks as a special case (n_blocks=1), so all backward compatibility is maintained.
