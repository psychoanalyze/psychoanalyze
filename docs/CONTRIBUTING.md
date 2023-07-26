# Contribute

*PsychoAnalyze* welcomes contributions, feature requests and bug reports from everyone!

If you are a researcher seeking to use PsychoAnalyze in your own research context, we'd love to hear from you!

- ✉️ [E-mail](mailto:t.schlic@wustl.edu)

- 🗣️ [Discussions](https://github.com/orgs/psychoanalyze/discussions) - Start an 💡[Idea](https://github.com/orgs/psychoanalyze/discussions/categories/ideas)

- 💻 [Feature Request](https://github.com/psychoanalyze/psychoanalyze/issues/new?assignees=&labels=enhancement&projects=&template=feature-request.md&title=%5BNEW%5D)

Otherwise, examine the [roadmap](https://github.com/orgs/psychoanalyze/projects/2) to see what we have planned!
## Feature Requests

PsychoAnalyze aims to be community-driven software. If you would like to use PsychoAnalyze in your own research context, please let us know what features you need to make that possible. Examine our roadmap to see what we already have planned, and open an issue using the "Feature Request" template to let us know what you need.

## Bug Reports

If you encounter a bug, please open an issue using the "Bug Report" template.

## Local Development Environment

!!! tip

Windows users will likely have more success following this guide if they use [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) as their command line interface. More thorough "pure"-Windows documentation is forthcoming.

### Option 1: Dev Container

The recommended way to set up a development environment is to use utilize our [Dev Container](https://containers.dev/) configuration to build a containerized environment. You may run a Dev Container in the cloud using GitHub Codespaces, or locally using Docker Desktop on OSX and Windows.

#### GitHub Codespaces

GitHub Codespaces is a cloud-based development environment that allows you to develop PsychoAnalyze without installing any software on your local machine. To use GitHub Codespaces, click the "Code" button at the top of the repository and select "Open with Codespaces". This will open a new Codespace in your browser. Once the Codespace is ready, you will be able to open a terminal and run one of our base commands.

#### Local Dev Container

Required: [Docker Desktop](https://www.docker.com/products/docker-desktop)

1. Clone the repository
2. Open the repository in VS Code
3. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
4. Use Ctrl+Shift+P to open the command palette and select "Remote-Containers: Reopen in Container" (or, accept the prompt from VS Code to do so).

### Option 2: Install dependencies manually

PsychoAnalyze uses

- Python 3.11
- [Poetry](https://python-poetry.org/) for package and virtual environment management
- [Pre-commit](https://pre-commit.com/) for automated code formatting, linting, type checking, and automated testing as part of a pre-commit workflow.

All other dependencies are defined in `pyproject.toml` and will be installed automatically in your active virtual environment when you run `poetry install`.

!!! tip

    Python and Poetry can be installed and managed with [`asdf`](https://asdf-vm.com/), an awesome environment management tool.
