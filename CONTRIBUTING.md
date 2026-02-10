# Contribute

*PsychoAnalyze* welcomes contributions, feature requests and bug reports from everyone!

If you are a researcher seeking to use PsychoAnalyze in your own research context, we'd love to help you get started!

Here are 3 suggested ways to

- 🧪 [Open a Feature Request](https://github.com/psychoanalyze/psychoanalyze/issues/new?assignees=&labels=enhancement&projects=&template=feature-request.md&title=%5BNEW%5D) - for well-posed suggestions.

- 💡[Start a Discussion](https://github.com/orgs/psychoanalyze/discussions) - For feedback on your idea for a new feature or use case.

- ✉️ [Send us an E-mail](mailto:t.schlic@wustl.edu)

Eager to contribute but not sure where to start? Check out our [roadmap](https://github.com/orgs/psychoanalyze/projects/2) to see what we have planned!

## Feature Requests

PsychoAnalyze aims to be community-driven software. If you would like to use PsychoAnalyze in your own research context, please let us know what features you need to make that possible. Examine our roadmap to see what we already have planned, and open an issue using the "Feature Request" template to let us know what you need.

## Bug Reports

If you encounter a bug, please open an issue using the "Bug Report" template.

## Developing

If you have experience working in Python, we'd love to have your help developing PsychoAnalyze! See our our page on [environment](environment.md) to set up your environment via Codespaces or otherwise. Familiarize yourself with the [API](api.md) and our [tests](tests.md). Then, consider picking up an [issue](https://github.com/psychoanalyze/psychoanalyze/issues) on GitHub! Write your tests first and get feedback if necessary. Submit a pull request to `main` when you believe a feature is ready to merge.

> Tip: no one's ever made a pull request that was too small and too easy to review 🙂

### Testing & CI

PsychoAnalyze uses pytest with Allure reporting for comprehensive test reports. When you submit a pull request:

1. **Automated Testing**: The CI workflow automatically runs all tests
2. **Allure Reports**: Test results are published as interactive Allure reports
   - **View Online**: Reports are deployed to GitHub Pages at `https://psychoanalyze.github.io/psychoanalyze/reports/`
   - **Download**: Reports are also available as workflow artifacts
3. **PR Comments**: A bot will comment on your PR with links to view the test report

To run tests locally with Allure reporting:
```bash
# Run tests and generate Allure results
uv run pytest tests/ --alluredir=allure-results

# Generate and view the Allure report (requires allure-commandline)
allure serve allure-results
```
