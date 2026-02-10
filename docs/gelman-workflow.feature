Feature: Gelman Bayesian Workflow in Dashboard
  As a researcher using the PsychoAnalyze dashboard
  I want to follow the Gelman Bayesian workflow
  So that I can build robust hierarchical models with proper diagnostics

  Background:
    Given the dashboard is running at "localhost:8080"
    And I have loaded trial data with "Intensity", "Result", "Block", "Subject"
    And PyMC and ArviZ are available

  # Step 1: Model Building and Prior Selection
  Scenario: Define prior distributions for psychometric parameters
    Given I am on the "Bayesian Analysis" tab
    When I select "Define Priors" mode
    Then I should see prior input controls for "threshold (x₀)"
    And I should see prior input controls for "slope (k)"
    And I should see prior input controls for "lapse rate (λ)"
    And I should see prior input controls for "guess rate (γ)"
    When I set "x₀" prior to "Normal(μ=100, σ=50)"
    And I set "k" prior to "HalfNormal(σ=2)"
    And I set "λ" prior to "Beta(α=1, β=9)"
    And I set "γ" prior to "Beta(α=1, β=9)"
    Then the prior specification should be displayed
    And I should see a "Run Prior Predictive Check" button

  Scenario: Configure hierarchical model structure
    Given I am on the "Bayesian Analysis" tab
    And I have defined priors
    When I select "Hierarchical Model" checkbox
    Then I should see population-level parameter controls
    And I should see subject-level parameter controls
    When I set population prior for "μ_x₀" to "Normal(μ=100, σ=100)"
    And I set population prior for "σ_x₀" to "HalfNormal(σ=50)"
    Then the hierarchical model specification should be displayed

  # Step 2: Prior Predictive Checks
  Scenario: Run prior predictive simulation
    Given I have specified all priors
    When I click "Run Prior Predictive Check"
    Then I should see a progress indicator
    And the system should generate "N=1000" prior predictive samples
    When the simulation completes
    Then I should see a prior predictive plot
    And the plot should show simulated psychometric curves
    And the plot should overlay observed data for comparison

  Scenario: Evaluate prior predictive fit
    Given I have prior predictive samples
    When I view the prior predictive plot
    Then I should see curves spanning a reasonable intensity range
    And I should see coverage of possible threshold values
    When the priors generate implausible curves
    Then I should see a warning message
    And I should be able to return to prior specification

  # Step 3: Model Fitting
  Scenario: Configure MCMC sampler
    Given I have validated priors
    When I navigate to "Fit Model" section
    Then I should see MCMC configuration controls
    And I should see "Number of chains" input (default: 4)
    And I should see "Draws per chain" input (default: 2000)
    And I should see "Tuning steps" input (default: 1000)
    And I should see "Target accept" input (default: 0.95)
    When I adjust sampler settings
    Then the configuration should update

  Scenario: Execute PyMC inference
    Given I have configured the sampler
    When I click "Run MCMC Sampling"
    Then I should see a real-time progress bar
    And I should see live chain statistics
    When sampling completes
    Then I should see a success message
    And posterior samples should be stored
    And I should see "View Diagnostics" button

  Scenario: Handle sampling errors
    Given I am running MCMC sampling
    When the sampler encounters divergences
    Then I should see a warning with divergence count
    And I should see recommendations to adjust "target_accept"
    When the sampler fails to converge
    Then I should see R-hat values greater than 1.01
    And I should see a suggestion to increase draws
    And I should be able to re-run with new settings

  # Step 4: Convergence Diagnostics
  Scenario: View trace plots
    Given I have completed MCMC sampling
    When I navigate to "Diagnostics" tab
    Then I should see trace plots for all parameters
    And trace plots should show all chains overlaid
    And I should see "x₀", "k", "λ", "γ" traces
    When I inspect a trace plot
    Then I should see good mixing (hairy caterpillar)
    And chains should overlap without drift

  Scenario: Check R-hat convergence statistics
    Given I am on the "Diagnostics" tab
    When I view the convergence table
    Then I should see R-hat values for all parameters
    And all R-hat values should be less than 1.01
    When a parameter has R-hat greater than 1.01
    Then that row should be highlighted in red
    And I should see a "Re-run Sampling" button

  Scenario: Check effective sample size
    Given I am on the "Diagnostics" tab
    When I view the convergence table
    Then I should see "n_eff" (effective sample size) for all parameters
    And "n_eff" should be greater than 1000 per parameter
    When "n_eff" is too low
    Then I should see a warning about insufficient posterior samples

  Scenario: Examine posterior distributions
    Given sampling has converged
    When I navigate to "Posterior" tab
    Then I should see density plots for all parameters
    And I should see "x₀" posterior distribution
    And I should see "k" posterior distribution
    When I hover over a distribution
    Then I should see mean, median, and 95% HDI
    And I should see the prior overlaid as a dashed line

  # Step 5: Posterior Predictive Checks
  Scenario: Run posterior predictive simulation
    Given I have converged posterior samples
    When I click "Run Posterior Predictive Check"
    Then the system should generate posterior predictive samples
    And I should see a progress indicator
    When simulation completes
    Then I should see posterior predictive plots

  Scenario: Compare observed vs posterior predictive data
    Given I have posterior predictive samples
    When I view the posterior predictive plot
    Then I should see observed data as points
    And I should see posterior predictive intervals as shaded bands
    And I should see the median posterior curve
    When the model fits well
    Then observed points should fall within predictive intervals
    When the model fits poorly
    Then I should see systematic deviations
    And I should see a warning about model misspecification

  Scenario: Check posterior predictive p-value
    Given I have posterior predictive samples
    When I navigate to "Model Checking" section
    Then I should see test statistics table
    And I should see "Bayesian p-value" for chi-square
    And I should see "Bayesian p-value" for deviance
    When p-values are between 0.05 and 0.95
    Then the test should be marked as "PASS"
    When p-values are extreme (< 0.05 or > 0.95)
    Then the test should be marked as "FAIL"
    And I should see a recommendation to revise the model

  # Step 6: Model Comparison
  Scenario: Fit alternative models for comparison
    Given I have a baseline model fit
    When I navigate to "Model Comparison" tab
    Then I should see a list of alternative model specifications
    And I should see "Non-hierarchical" model option
    And I should see "Fixed lapse/guess" model option
    And I should see "Subject-specific slopes" model option
    When I select an alternative model
    And I click "Fit Alternative Model"
    Then the model should be fit with MCMC
    And results should be added to the comparison table

  Scenario: Compare models using WAIC
    Given I have fit multiple models
    When I view the "Model Comparison" table
    Then I should see WAIC scores for each model
    And I should see WAIC standard errors
    And I should see ΔWAIC (difference from best model)
    And models should be ranked by WAIC (lower is better)
    When I hover over WAIC values
    Then I should see a tooltip explaining the metric

  Scenario: Compare models using LOO-CV
    Given I have fit multiple models
    When I view the "Model Comparison" table
    Then I should see LOO-CV scores for each model
    And I should see number of Pareto-k warnings
    When a model has many Pareto-k warnings (> 10%)
    Then that row should be flagged
    And I should see a note that LOO may be unreliable

  # Step 7: Sensitivity Analysis
  Scenario: Vary priors to test robustness
    Given I have a baseline model fit
    When I navigate to "Sensitivity Analysis" tab
    Then I should see prior sensitivity controls
    When I select "Vary x₀ prior width"
    And I set sensitivity range to "σ ∈ [25, 100]"
    And I click "Run Sensitivity Analysis"
    Then multiple models should be fit with different priors
    And I should see a sensitivity plot
    And posterior means should be plotted vs prior width

  Scenario: Evaluate sensitivity results
    Given I have run sensitivity analysis
    When I view the sensitivity plot
    Then I should see how posterior estimates change with priors
    When posterior estimates are stable across prior choices
    Then I should see a "Robust" indicator
    When posterior estimates vary substantially
    Then I should see a "Sensitive" warning
    And I should consider gathering more data

  # Step 8: Export and Report
  Scenario: Generate Bayesian workflow report
    Given I have completed all workflow steps
    When I click "Generate Report"
    Then I should see a report preview
    And the report should include prior specifications
    And the report should include convergence diagnostics
    And the report should include posterior summaries
    And the report should include posterior predictive checks
    And the report should include model comparison tables
    When I click "Download Report"
    Then a PDF should be generated
    And the PDF should include all plots and tables

  Scenario: Export posterior samples for further analysis
    Given I have converged posterior samples
    When I navigate to "Export" section
    Then I should see "Export to ArviZ (NetCDF)" button
    And I should see "Export to CSV" button
    When I click "Export to ArviZ (NetCDF)"
    Then an InferenceData object should be saved
    And I should see a confirmation message with file path
    When I click "Export to CSV"
    Then posterior draws should be saved as CSV
    And the CSV should include all parameters and chains

  # Step 9: Interactive Exploration
  Scenario: Explore subject-level parameters
    Given I have fit a hierarchical model
    When I navigate to "Subject Parameters" tab
    Then I should see a table of subject-level estimates
    And I should see "x₀_subject" for each subject (U, Y, Z)
    And I should see 95% credible intervals
    When I click on a subject row
    Then I should see detailed posterior plots for that subject
    And I should see how subject-level estimates relate to population mean

  Scenario: Visualize hierarchical shrinkage
    Given I have fit a hierarchical model
    When I navigate to "Hierarchical Structure" tab
    Then I should see a shrinkage plot
    And the plot should show subject-level estimates vs pooled estimates
    And I should see how hierarchical model pulls outliers toward population mean
    When I hover over a subject point
    Then I should see subject ID and estimate values

  # Error Handling
  Scenario: Handle insufficient data warning
    Given I am on the "Bayesian Analysis" tab
    When I have fewer than 50 trials
    Then I should see a warning about insufficient data
    And I should see a recommendation to use more informative priors
    And I should still be able to proceed with analysis

  Scenario: Handle numerical stability issues
    Given I am running MCMC sampling
    When the sampler encounters numerical instability
    Then I should see an error message
    And I should see suggestions to reparameterize the model
    And I should be able to enable "use_centered_parameterization" option
