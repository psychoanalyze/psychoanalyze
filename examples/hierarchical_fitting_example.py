"""Example: Hierarchical Model for Psychometric Function Fitting.

This example demonstrates the key benefits of hierarchical modeling for
psychometric function fitting, comparing it to independent block fits.
"""

import numpy as np
import polars as pl

from psychoanalyze.data import blocks, hierarchical, trials


def generate_multi_block_data(n_blocks: int = 5) -> pl.DataFrame:
    """Generate simulated data for multiple blocks.
    
    Simulates a scenario where:
    - All blocks share similar psychometric parameters (same population)
    - Some blocks have more trials than others (varying data quality)
    - True threshold is around 0.0 for all blocks
    """
    np.random.seed(42)
    all_trials = []
    
    for block_id in range(n_blocks):
        # Vary number of trials per block (some sparse, some well-sampled)
        if block_id == 0:
            n_trials = 100  # Well-sampled reference block
        elif block_id in [1, 2]:
            n_trials = 50   # Moderately sampled
        else:
            n_trials = 10   # Sparse blocks
        
        # Generate trials with slight variation in parameters
        true_threshold = 0.0 + np.random.normal(0, 0.2)
        true_slope = 1.0 + np.random.normal(0, 0.1)
        
        x = np.random.uniform(-2, 2, n_trials)
        p = 1 / (1 + np.exp(-(x - true_threshold) / true_slope))
        y = (np.random.random(n_trials) < p).astype(int)
        
        block_trials = pl.DataFrame({
            "Intensity": x,
            "Result": y,
            "Block": [block_id] * n_trials,
        })
        all_trials.append(block_trials)
    
    return pl.concat(all_trials)


def compare_fitting_approaches():
    """Compare independent vs hierarchical fitting approaches."""
    print("=" * 70)
    print("Comparing Independent vs Hierarchical Fitting Approaches")
    print("=" * 70)
    
    # Generate data
    print("\n1. Generating multi-block data...")
    trials_df = generate_multi_block_data(n_blocks=5)
    print(f"   Total trials: {len(trials_df)}")
    print(f"   Blocks: {trials_df['Block'].unique().sort().to_list()}")
    
    # Get trial counts per block
    block_sizes = (
        trials_df.group_by("Block")
        .agg(pl.len().alias("n_trials"))
        .sort("Block")
    )
    print("\n   Trials per block:")
    for row in block_sizes.iter_rows(named=True):
        print(f"     Block {row['Block']}: {row['n_trials']} trials")
    
    # Approach 1: Independent fits
    print("\n2. Independent Fits (legacy approach)...")
    print("   Fitting each block separately...")
    independent_results = []
    
    for block_id in sorted(trials_df["Block"].unique().to_list()):
        block_trials = trials_df.filter(pl.col("Block") == block_id)
        try:
            idata = blocks.fit(
                block_trials,
                draws=200,
                tune=200,
                chains=1,
                random_seed=42,
            )
            summary = blocks.summarize_fit(idata)
            independent_results.append({
                "block": block_id,
                "threshold": summary["threshold"],
                "slope": summary["slope"],
            })
        except Exception as e:
            print(f"   Warning: Block {block_id} failed to fit: {e}")
            independent_results.append({
                "block": block_id,
                "threshold": np.nan,
                "slope": np.nan,
            })
    
    print("\n   Independent fit results:")
    print("   Block | Threshold | Slope")
    print("   ------|-----------|-------")
    for result in independent_results:
        print(f"   {result['block']:5d} | {result['threshold']:9.3f} | {result['slope']:5.3f}")
    
    # Approach 2: Hierarchical fit
    print("\n3. Hierarchical Fit (new approach)...")
    print("   Fitting all blocks jointly with information sharing...")
    hierarchical_idata = hierarchical.fit(
        trials_df,
        draws=200,
        tune=200,
        chains=1,
        random_seed=42,
    )
    hierarchical_summary = hierarchical.summarize_fit(hierarchical_idata)
    
    print("\n   Group-level parameters (population estimates):")
    print(f"   μ_threshold: {-hierarchical_summary['mu_intercept'] / hierarchical_summary['mu_slope']:.3f}")
    print(f"   σ_intercept: {hierarchical_summary['sigma_intercept']:.3f}")
    print(f"   σ_slope:     {hierarchical_summary['sigma_slope']:.3f}")
    
    print("\n   Block-specific parameters:")
    print("   Block | Threshold | Slope")
    print("   ------|-----------|-------")
    for i, block_id in enumerate(sorted(trials_df["Block"].unique().to_list())):
        print(f"   {block_id:5d} | {hierarchical_summary['threshold'][i]:9.3f} | {hierarchical_summary['slope'][i]:5.3f}")
    
    # Compare results
    print("\n4. Comparison: Effect of Hierarchical Modeling")
    print("   Block | Trials | Independent | Hierarchical | Difference")
    print("   ------|--------|-------------|--------------|------------")
    for i, result in enumerate(independent_results):
        block_id = result["block"]
        n_trials = block_sizes.filter(pl.col("Block") == block_id)["n_trials"][0]
        indep_thresh = result["threshold"]
        hier_thresh = hierarchical_summary["threshold"][i]
        diff = hier_thresh - indep_thresh
        
        print(f"   {block_id:5d} | {n_trials:6d} | {indep_thresh:11.3f} | {hier_thresh:12.3f} | {diff:10.3f}")
    
    print("\n5. Key Observations:")
    print("   - Well-sampled blocks (Block 0): Similar estimates")
    print("   - Sparse blocks (Block 3, 4): More shrinkage toward group mean")
    print("   - Hierarchical model provides regularization for sparse data")
    print("   - Group-level parameters estimate population characteristics")
    
    print("\n" + "=" * 70)


def demonstrate_credible_bands():
    """Demonstrate computing credible bands for psychometric curves."""
    print("\n" + "=" * 70)
    print("Computing Credible Bands for Psychometric Curves")
    print("=" * 70)
    
    # Generate simple two-block data
    trials_df = pl.DataFrame({
        "Intensity": [-2, -1, 0, 1, 2] * 2,
        "Result": [0, 0, 0, 1, 1, 0, 0, 1, 1, 1],
        "Block": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    })
    
    print("\n1. Fitting hierarchical model...")
    idata = hierarchical.fit(
        trials_df,
        draws=200,
        tune=200,
        chains=1,
        random_seed=42,
    )
    
    print("\n2. Computing credible bands for each block...")
    x = np.linspace(-3, 3, 50)
    
    for block_idx in [0, 1]:
        band = hierarchical.curve_credible_band(
            idata,
            x,
            block_idx=block_idx,
            hdi_prob=0.9,
        )
        
        print(f"\n   Block {block_idx}:")
        print(f"   - Intensity range: [{x.min():.1f}, {x.max():.1f}]")
        print(f"   - Band covers 90% credible interval")
        # Find closest point to x=0
        closest_idx = int(np.abs(band["Intensity"].to_numpy()).argmin())
        print(f"   - Lower bound at x≈0: {band['lower'][closest_idx]:.3f}")
        print(f"   - Upper bound at x≈0: {band['upper'][closest_idx]:.3f}")
    
    print("\n" + "=" * 70)


def demonstrate_points_interface():
    """Demonstrate using aggregated points data."""
    print("\n" + "=" * 70)
    print("Using Aggregated Points Data")
    print("=" * 70)
    
    # Create points-level data directly
    points_df = pl.DataFrame({
        "Intensity": [-1.0, 0.0, 1.0, -1.0, 0.0, 1.0],
        "Hits": [2, 5, 8, 1, 6, 9],
        "n trials": [10, 10, 10, 10, 10, 10],
        "Block": [0, 0, 0, 1, 1, 1],
    })
    
    print("\n1. Points data (aggregated):")
    print(points_df)
    
    print("\n2. Fitting hierarchical model from points...")
    idata = hierarchical.from_points(
        points_df,
        draws=200,
        tune=200,
        chains=1,
        random_seed=42,
    )
    
    summary = hierarchical.summarize_fit(idata)
    
    print("\n3. Results:")
    print(f"   Group threshold: {-summary['mu_intercept'] / summary['mu_slope']:.3f}")
    print(f"   Block 0 threshold: {summary['threshold'][0]:.3f}")
    print(f"   Block 1 threshold: {summary['threshold'][1]:.3f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run demonstrations
    compare_fitting_approaches()
    demonstrate_credible_bands()
    demonstrate_points_interface()
    
    print("\n✅ All examples completed successfully!")
    print("\nFor more information, see: docs/hierarchical_model.md")
