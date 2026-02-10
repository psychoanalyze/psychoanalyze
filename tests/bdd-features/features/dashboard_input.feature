Feature: Dashboard input data selection
  As a dashboard user
  I want to choose the active dataset via upload
  So that the dashboard analyzes my trials

  Background:
    Given the dashboard is running

  Scenario: Upload a CSV trials table
    Given I have a trials table in CSV format
    When I upload the dataset
    Then the dataset should load as the active trials table

  Scenario: Upload a Parquet trials table
    Given I have a trials table in Parquet format
    When I upload the dataset
    Then the dataset should load as the active trials table

  Scenario: Reject uploads missing required columns
    Given I have a dataset missing one or more required columns
    When I upload the dataset
    Then I should see an error indicating required columns are missing

  Scenario: Subject column is optional
    Given I have trial data with columns "Block", "Intensity", and "Result"
    When I upload the dataset
    Then the dataset should load as the active trials table
