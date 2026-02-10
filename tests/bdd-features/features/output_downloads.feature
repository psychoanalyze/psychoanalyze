Feature: Output downloads
  As a dashboard user
  I want to download plots and data in standard formats
  So that I can share results and run offline analysis

  Background:
    Given the dashboard is running
    And a plot is visible in the Visualization Panel
    And an active dataset is loaded

  Scenario: Download current plot as SVG
    When I download the current plot as SVG
    Then I should receive an SVG file

  Scenario: Download current plot as PNG
    When I download the current plot as PNG
    Then I should receive a PNG file

  Scenario: Download current plot as PDF
    When I download the current plot as PDF
    Then I should receive a PDF file

  Scenario: Download active data as CSV zip
    When I download the active data as CSV zip
    Then I should receive a ZIP file containing CSV exports

  Scenario: Download active data as JSON
    When I download the active data as JSON
    Then I should receive a JSON file

  Scenario: Download active data as Parquet
    When I download the active data as Parquet
    Then I should receive a Parquet file

  Scenario: Download active data as DuckDB
    When I download the active data as DuckDB
    Then I should receive a DuckDB database file
