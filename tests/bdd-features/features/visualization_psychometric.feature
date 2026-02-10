Feature: Psychometric visualization panel
  As a dashboard user
  I want an interactive psychometric function plot
  So that I can explore the relationship between intensity and response probability

  Background:
    Given the dashboard is running
    And psychometric data are available

  Scenario: Psychometric plot supports interactive inspection
    When I view the psychometric function plot
    Then I should be able to zoom and pan
    And I should be able to hover over points to see their values

  Scenario: Fitted curves include a Bayesian credible band
    When fitted psychometric curves are displayed
    Then the fitted curves should include a shaded Bayesian 90% credible band
