Feature: Psychophysical Data Simulation
  As a psychophysics researcher
  I want to simulate and analyze experimental trials
  So that I can understand threshold detection and psychometric function behavior

  Background:
        Given a psychometric function with a given threshold and slope
        And a stimulus intensity range from 0 to a positive value

  Scenario: Psychometric curve updates after each trial
    Given an empty trial dataset
        And empty plots on a dashboard
    When I start an online simulation session
        And I simulate presentation of stimuli using the Method of Constant Stimuli for a go/no-go task
    Then the psychometric curve should update after each trial

  Scenario: Threshold estimate converges toward the true threshold
    Given an empty trial dataset
        And empty plots on a dashboard
    When I start an online simulation session
        And I simulate presentation of stimuli using the Method of Constant Stimuli for a go/no-go task
    Then the threshold estimate should converge toward the true threshold over time

  Scenario: Visualization renders within 100ms per update
    Given an empty trial dataset
        And empty plots on a dashboard
    When I start an online simulation session
        And I simulate presentation of stimuli using the Method of Constant Stimuli for a go/no-go task
    Then the visualization should render within 100ms per update

  Scenario: Fitted curve uncertainty narrows with more trials
    Given an empty trial dataset
        And empty plots on a dashboard
    When I start an online simulation session
        And I simulate presentation of stimuli using the Method of Constant Stimuli for a go/no-go task
    Then the fitted curve confidence interval should narrow with more trials

  Scenario: Simulation stops after threshold stabilizes
    Given an empty trial dataset
        And empty plots on a dashboard
    When I start an online simulation session
        And I simulate presentation of stimuli using the Method of Constant Stimuli for a go/no-go task
    Then the simulation should stop when the threshold estimate stabilizes within a predefined range
