Feature: Psychometric Data Pipeline
  As a researcher
  I want to transform trial data through the analysis pipeline
  So that I can produce accurate psychometric plots

  Background:
    Given the psychoanalyze data contract is valid
    And all required schemas are defined

  Scenario: Transform trials to points
    Given I have trial data with columns "Intensity", "Result", "Block"
    When I aggregate trials by "Intensity"
    Then I should get points with "Hits", "n trials", "Hit Rate"
    And "Hit Rate" should equal "Hits / n trials"
    And binomial confidence intervals should be calculated

  Scenario: Fit psychometric function to points
    Given I have points data with "Intensity" and "Hit Rate"
    When I perform logistic regression
    Then I should get block parameters with "threshold", "slope", "intercept"
    And "threshold" should equal "-intercept / slope"
    And the fitted curve should pass the goodness-of-fit test

  Scenario: Generate intensity views
    Given I have raw "Intensity" values
    When I derive intensity views
    Then I should get "Intensity_raw", "Intensity_log", "Intensity_z"
    And "Intensity_log" should equal "log(Intensity_raw)"
    And "Intensity_z" should be standardized with mean 0 and std 1

  Scenario: Join blocks to sessions for longitudinal analysis
    Given I have blocks with "Block", "threshold", "Subject"
    And I have sessions with "Session", "Date", "Days Since Implant", "Block IDs"
    When I join blocks to sessions
    Then I should get longitudinal data with "Days", "threshold_mean", "Subject"
    And confidence intervals should be calculated per day

  Scenario: Compute Weber parameters from JND estimates
    Given I have JND estimates with "Standard", "threshold", "Weber fraction"
    When I fit a power law "log(ΔI) ~ β·log(I)"
    Then I should get Weber parameters with "k", "β", "R²"
    And "β" should be in the range [0.8, 1.1] for near-miss

  Scenario: Compute strength-duration parameters
    Given I have PW thresholds with "Pulse Width", "threshold"
    When I fit the Weiss-Lapicque equation "I = Irh + (Irh·τ / PW)"
    Then I should get S-D parameters with "Irh", "τ", "charge_threshold"
    And "Irh" should be positive
    And "τ" should be positive

  Scenario: Run Bayesian hierarchical model
    Given I have trials with "Intensity", "Result", "Block", "Subject"
    When I run PyMC inference
    Then I should get MCMC samples with "iteration", "chain", "x₀", "k"
    And I should get posterior summary with "mean", "sd", "2.5%", "97.5%", "n_eff", "Rhat"
    And "Rhat" should be less than 1.01 for convergence
    And I should get hierarchical params with "x₀_subject", "μ_x₀", "σ_x₀"

  Scenario: Generate psychometric function plot
    Given I have points with "Intensity", "Hit Rate", "ci_low", "ci_high"
    And I have blocks with "threshold", "slope", "intercept", "Subject"
    And I have intensity views with transformed scales
    When I generate the psychometric function plot
    Then the x-axis should display "Intensity (selectable scale)"
    And the y-axis should display "Hit Rate [0, 1]"
    And observed points should be rendered as scatter markers
    And the fitted curve should use the formula "ψ(x) = γ + (1-γ-λ)*F(x; x₀, k)"
    And a vertical threshold line should appear at "x₀"
    And error bars should use binomial CI
    And colors should map to "Subject" using the colormap

  Scenario: Generate threshold vs time plot
    Given I have longitudinal data with "Days", "threshold_mean", "threshold_ci_low", "threshold_ci_high", "Subject"
    And I have time views with transformed scales
    When I generate the threshold vs time plot
    Then the x-axis should display "Time (selectable scale)"
    And the y-axis should display "Threshold Amplitude (μA)"
    And threshold points should be colored by "Subject"
    And confidence bands should render using CI values

  Scenario: Generate Weber curves plot
    Given I have JND estimates with "Standard", "threshold", "Weber fraction", "Subject"
    And I have Weber parameters with "k", "β"
    And I have standard views with transformed scales
    When I generate the Weber curves plot
    Then the x-axis should display "Standard Intensity (selectable scale)"
    And the y-axis should display "ΔI (JND, μA)"
    And JND points should be rendered as scatter markers
    And the Weber line should follow "ΔI = k·I"
    And the near-miss curve should follow "ΔI = k·I^β"

  Scenario: Generate strength-duration plot
    Given I have PW thresholds with "Pulse Width", "threshold", "Subject"
    And I have S-D parameters with "Irh", "τ"
    And I have PW views with transformed scales
    When I generate the strength-duration plot
    Then the x-axis should display "Pulse Width (selectable scale)"
    And the y-axis should display "Threshold Current (μA)"
    And threshold points should be rendered as scatter markers
    And the S-D curve should follow "I = Irh + (Irh·τ / PW)"
    And a chronaxie marker should appear at "τ"
    And a horizontal asymptote should appear at "Irh"

  Scenario: Generate Bayes analysis plot
    Given I have PyMC samples with "x₀", "k"
    And I have posterior summary with "mean", "2.5%", "97.5%"
    And I have hierarchical params with "Subject"
    And I have parameter views with transformed scales
    When I generate the Bayes analysis plot
    Then the x-axis should display "Parameter value (x₀, k, or hierarchical)"
    And the y-axis should display "Posterior density p(θ|data)"
    And the posterior distribution should be rendered as a density plot
    And credible intervals should be shaded at "95% HDI"
    And point estimates should appear at posterior "mean"
    And plots should use ArviZ for diagnostics

  Scenario Outline: Toggle plot scale controls
    Given I have a plot with "<axis>" data
    When I set "x_scale" to "<scale>"
    And I set "x_units" to "<units>"
    Then the x-axis should display data in "<scale>" scale
    And the x-axis should use "<units>" representation

    Examples:
      | axis           | scale  | units   |
      | Intensity      | linear | raw     |
      | Intensity      | log    | raw     |
      | Intensity      | linear | z-score |
      | Days           | log    | z-score |
      | Standard       | log    | raw     |
      | Pulse Width    | linear | z-score |
      | Parameter      | log    | z-score |

  Scenario: Validate data contract compliance
    Given the data contract at "psychoanalyze-data-contract.odcs.yaml"
    When I validate all data tables against the contract
    Then "trials" should match the trials schema
    And "points" should match the points schema
    And "blocks" should match the blocks schema
    And "sessions" should match the sessions schema
    And all derived views should match their respective schemas
    And all required fields should be present
    And all data types should conform to the contract
