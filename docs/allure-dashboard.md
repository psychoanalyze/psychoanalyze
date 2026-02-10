# Allure Dashboard

[Allure](https://docs.qameta.io/allure/) is a test reporting framework that provides a comprehensive visual representation of test results and test execution history.

## Quick Start

### Generate Test Report and Open Dashboard

```bash
nu scripts/allure/generate.nu
```

This will:
1. Run all tests with Allure reporter enabled
2. Generate the Allure report in `.allure/report/`
3. Display report location

### Serve Report Locally

```bash
nu scripts/allure/serve.nu
```

This starts a local development server at `http://localhost:4040` with the latest Allure report.

### View Report History

Allure stores historical data in `.allure/history/`. This allows the dashboard to show trends over time:

```bash
# Clear history to start fresh
rm -r .allure/history/

# Then regenerate the report
nu scripts/allure/generate.nu
```

## Features

### Overview Dashboard
- **Quick statistics**: Pass/fail rate, test execution duration
- **Flaky tests**: Identify unstable tests
- **Test timeline**: Visual representation of test execution

### Test Details
- **Test steps**: Breakdown of each test with detailed steps
- **Attachments**: Plots, dataframes, or other test artifacts
- **Error messages**: Full stack traces with context
- **Parameters**: Test parameters and input data variations

### Trends
- **Historical graphs**: Track pass rate over time
- **Execution duration**: Monitor performance of tests
- **Flakiness metrics**: See which tests are most unstable

## Configuration

### Pytest Markers

Tests can be marked for better organization in Allure:

```python
import pytest

@pytest.mark.unit
def test_simple_function():
    assert True

@pytest.mark.integration
def test_data_loading():
    assert True

@pytest.mark.slow
def test_heavy_computation():
    assert True
```

Available markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.psychometric` - Psychometric function tests
- `@pytest.mark.data` - Data manipulation tests
- `@pytest.mark.analysis` - Statistical analysis tests

### Custom Step Reporting

Add detailed steps to your tests:

```python
import allure

def test_with_steps():
    with allure.step("Step 1: Load data"):
        df = load_trials()

    with allure.step("Step 2: Fit model"):
        params = fit(df)

    with allure.step("Step 3: Validate results"):
        assert params is not None
```

### Attach Artifacts

Attach files, images, or data to test reports:

```python
import allure

def test_with_attachment(trials_df):
    results = aggregate(trials_df)

    # Attach CSV
    allure.attach(
        results.to_csv(),
        name="aggregated_results.csv",
        attachment_type=allure.attachment_type.CSV
    )

    # Attach HTML table
    allure.attach(
        results.to_html(),
        name="results_table",
        attachment_type=allure.attachment_type.HTML
    )
```

## Integration with CI/CD

### GitHub Actions

Add to your workflow to collect Allure reports:

```yaml
- name: Run tests with Allure
  run: uv run pytest tests/ --alluredir=.allure/results

- name: Generate Allure Report
  if: always()
  run: allure generate .allure/results --clean -o .allure/report

- name: Upload report as artifact
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: allure-report
    path: .allure/report/
```

## Troubleshooting

### Report not generating
Ensure Allure CLI is installed:
```bash
uv run --with allure-pytest --with allure-behave -- allure --version
```

### Server failing to start
Check if port 4040 is available:
```bash
# Use custom port
nu scripts/allure/serve.nu --port 8080
```

### Clear cache
Remove generated data and regenerate:
```bash
rm -r .allure/results .allure/report .allure/history/
nu scripts/allure/generate.nu
```

## Resources

- [Allure Documentation](https://docs.qameta.io/allure/)
- [Allure Pytest Plugin](https://docs.qameta.io/allure-testops/ecosystem/pytest/)
- [Best Practices](https://docs.qameta.io/allure-testops/workflow/test-analysis/best-practices/)
