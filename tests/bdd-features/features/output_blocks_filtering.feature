Feature: Output blocks filtering
  As a dashboard user
  I want to filter plotted fits by selecting blocks
  So that I can focus on specific experimental segments

  Background:
    Given the dashboard is running
    And block-level threshold estimates are displayed in the Blocks chart

  Scenario: Filter plotted fits by selecting a block bar
    Given multiple blocks are available
    When I select one or more bars in the Blocks chart
    Then the plotted fits should be filtered to the selected blocks

  Scenario: Filter aggregated points by selecting a block bar
    Given aggregated points are displayed for the active dataset
    When I select one or more bars in the Blocks chart
    Then the aggregated points used in the visualization should be filtered to the selected blocks
