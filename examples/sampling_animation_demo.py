"""Example notebook demonstrating PyMC sampling animation.

This notebook shows how to use the AnimatedSampler to visualize
the evolution of MCMC sampling with pause/rewind capabilities.
"""
import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium", app_title="PyMC Sampling Animation Demo")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import polars as pl
    
    from psychoanalyze.animation import AnimatedSampler
    from psychoanalyze.animation.plot import (
        plot_multi_chain_traces,
        plot_posterior_evolution,
        plot_psychometric_curve_evolution,
        plot_sampling_dashboard,
        plot_trace_evolution,
    )
    return (
        AnimatedSampler,
        mo,
        np,
        pl,
        plot_multi_chain_traces,
        plot_posterior_evolution,
        plot_psychometric_curve_evolution,
        plot_sampling_dashboard,
        plot_trace_evolution,
    )


@app.cell
def _(mo):
    mo.md(
        """
        # PyMC Sampling Animation Demo
        
        This notebook demonstrates the animated PyMC sampler with pause/rewind capabilities.
        
        ## 1. Generate Sample Data
        
        First, we'll generate some sample psychophysics trial data.
        """
    )
    return


@app.cell
def _(np, pl):
    # Generate sample trial data
    n_trials = 100
    true_threshold = 1.5
    true_slope = 1.0
    
    np.random.seed(42)
    intensities = np.random.uniform(0, 3, n_trials)
    logits = -true_threshold * true_slope + true_slope * intensities
    probs = 1 / (1 + np.exp(-logits))
    results = (np.random.uniform(0, 1, n_trials) < probs).astype(int)
    
    trials_df = pl.DataFrame({
        "Intensity": intensities,
        "Result": results,
    })
    
    trials_df.head()
    return intensities, logits, n_trials, probs, results, trials_df, true_slope, true_threshold


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. Initialize Animated Sampler
        
        Create an AnimatedSampler with the trial data.
        """
    )
    return


@app.cell
def _(AnimatedSampler, trials_df):
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=500,
        tune=500,
        chains=2,
        cores=1,
        random_seed=42,
    )
    return (sampler,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. Run Sampling with Snapshots
        
        Sample the posterior and create snapshots at regular intervals.
        This allows us to "rewind" and view the sampling process.
        """
    )
    return


@app.cell
def _(sampler):
    idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=25)
    print(f"Sampling complete! Created {len(snapshots)} snapshots.")
    return idata, snapshots


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Interactive Draw Selector
        
        Use the slider to navigate through different sampling draws.
        The visualizations below will update to show the state at that draw.
        """
    )
    return


@app.cell
def _(mo, sampler):
    draw_slider = mo.ui.slider(
        start=10,
        stop=sampler.draws,
        value=sampler.draws,
        step=10,
        label="Draw Number",
        show_value=True,
    )
    draw_slider
    return (draw_slider,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Chain Selector
        
        Select which chain to visualize.
        """
    )
    return


@app.cell
def _(mo, sampler):
    chain_selector = mo.ui.dropdown(
        options={f"Chain {i}": i for i in range(sampler.chains)},
        value=0,
        label="Select Chain",
    )
    chain_selector
    return (chain_selector,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Trace Evolution
        
        Watch how the parameter trace evolves over the sampling draws.
        """
    )
    return


@app.cell
def _(chain_selector, draw_slider, plot_trace_evolution, sampler):
    trace_fig = plot_trace_evolution(
        sampler,
        param_name="threshold",
        chain=chain_selector.value,
        up_to_draw=draw_slider.value,
    )
    trace_fig
    return (trace_fig,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Posterior Distribution Evolution
        
        See how the posterior distribution builds up as more samples are collected.
        """
    )
    return


@app.cell
def _(chain_selector, draw_slider, plot_posterior_evolution, sampler):
    posterior_fig = plot_posterior_evolution(
        sampler,
        param_name="threshold",
        chain=chain_selector.value,
        up_to_draw=draw_slider.value,
    )
    posterior_fig
    return (posterior_fig,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. Psychometric Curve Evolution
        
        Watch the fitted psychometric curve evolve as the sampler explores the posterior.
        """
    )
    return


@app.cell
def _(chain_selector, draw_slider, plot_psychometric_curve_evolution, sampler, trials_df):
    curve_fig = plot_psychometric_curve_evolution(
        sampler,
        trials=trials_df,
        up_to_draw=draw_slider.value,
        chain=chain_selector.value,
        n_curves=30,
    )
    curve_fig
    return (curve_fig,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 9. Multi-Chain Convergence
        
        View all chains simultaneously to assess convergence.
        """
    )
    return


@app.cell
def _(draw_slider, plot_multi_chain_traces, sampler):
    multichain_fig = plot_multi_chain_traces(
        sampler,
        param_name="threshold",
        up_to_draw=draw_slider.value,
    )
    multichain_fig
    return (multichain_fig,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 10. Comprehensive Dashboard
        
        All-in-one view with traces, posterior, and fitted curve.
        """
    )
    return


@app.cell
def _(chain_selector, draw_slider, plot_sampling_dashboard, sampler, trials_df):
    dashboard_fig = plot_sampling_dashboard(
        sampler,
        trials=trials_df,
        up_to_draw=draw_slider.value,
        chain=chain_selector.value,
    )
    dashboard_fig
    return (dashboard_fig,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 11. Rewind Demonstration
        
        Use the rewind feature to go back to a specific sampling draw.
        """
    )
    return


@app.cell
def _(mo):
    rewind_draw = mo.ui.number(
        start=0,
        stop=500,
        value=100,
        step=10,
        label="Rewind to draw",
    )
    rewind_draw
    return (rewind_draw,)


@app.cell
def _(rewind_draw, sampler):
    snapshot = sampler.rewind_to(draw=rewind_draw.value, chain=0)
    if snapshot is not None:
        print(f"Rewound to draw {snapshot.draw} (chain {snapshot.chain})")
        print(f"Threshold samples collected: {len(snapshot.posterior_samples['threshold'])}")
    else:
        print(f"No snapshot available at draw {rewind_draw.value}")
    return (snapshot,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 12. Save/Load Snapshots
        
        Snapshots can be saved to disk and loaded later for replay.
        """
    )
    return


@app.cell
def _():
    from pathlib import Path
    import tempfile
    
    # Example of saving (commented out to avoid file I/O in demo)
    # save_path = Path(tempfile.gettempdir()) / "sampling_snapshots"
    # sampler.save_snapshots(save_path)
    # print(f"Snapshots saved to {save_path}")
    
    # Example of loading
    # new_sampler = AnimatedSampler(trials=trials_df, draws=500, tune=500, chains=2)
    # new_sampler.load_snapshots(save_path)
    # print("Snapshots loaded successfully")
    return Path, tempfile


if __name__ == "__main__":
    app.run()
