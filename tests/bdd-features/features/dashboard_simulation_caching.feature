Feature: Dashboard simulation regeneration and caching
  As a dashboard user
  I want simulation changes to be fast and repeatable
  So that I can explore model behavior interactively

  Background:
    Given the dashboard is running
    And the dashboard is using simulated trial data

  Scenario: Regenerate simulated trials when a parameter changes
    Given the current simulation parameters are displayed
    When I change a simulation parameter
    Then the simulation should regenerate trials in memory

  Scenario: Cache Bayesian fit artifacts on disk
    Given Bayesian fit results are available for the current simulation
    When I re-run the simulation with the same parameters
    Then the dashboard should load fit results from the local cache at "__marimo__/cache/psychoanalyze"
