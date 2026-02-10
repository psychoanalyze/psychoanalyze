---
description: "Prefer MCP tools over shell commands when available. Check tool availability before falling back to terminal."
applyTo: "**"
---

# Prefer MCP Tools Over Shell Commands

## Core Principle

**Always check whether an MCP tool exists for an operation before running it as a shell command.** MCP tools provide structured input/output, better error handling, and integrate directly with the editor — shell commands should be the fallback, not the default.

## Tool Availability Mapping

### JJ (Jujutsu) — use `mcp_jj_*` tools

| Shell command | MCP tool | Notes |
|---|---|---|
| `jj describe -m "..."` | `mcp_jj_describe` | Set revision message |
| `jj abandon <rev>` | `mcp_jj_abandon` | Discard revisions |
| `jj edit <rev>` | `mcp_jj_edit` | Switch working copy |
| `jj new -m "..."` | activate `revision_management_tools` → `mcp_jj_new` | Create new revision |
| `jj commit -m "..."` | activate `revision_management_tools` → `mcp_jj_commit` | Commit current changes |
| `jj rebase ...` | activate `revision_management_tools` → `mcp_jj_rebase` | Move revisions |
| `jj show` | activate `revision_management_tools` → `mcp_jj_show` | Inspect revision |
| `jj diff` | activate `diff_and_annotation_tools` → `mcp_jj_diff` | Compare revisions |
| `jj log` | activate `revision_management_tools` → `mcp_jj_log` | View history |
| `jj git push` | activate `bookmark_management_tools` → `mcp_jj_git-push` | Push to remote |
| `jj git import` | `mcp_jj_git-import` | Sync Git → JJ |
| `jj git export` | `mcp_jj_git-export` | Sync JJ → Git |
| `jj config set ...` | `mcp_jj_config-set` | Set config option |
| `jj file track ...` | `mcp_jj_file-track` | Track files |
| `jj file chmod ...` | `mcp_jj_file-chmod` | Set executable bit |

**Activation pattern:** Some jj tools require activation first. Call the appropriate `activate_*_tools` function, then use the unlocked tool.

### UV / Python — use built-in Python tools

| Shell command | Tool | Notes |
|---|---|---|
| `uv run pytest` | `runTests` | Structured test output with pass/fail details |
| `uv add <pkg>` | `activate_dependency_management_tools` → `add_package` | Adds to pyproject.toml |
| `uv add --dev <pkg>` | `activate_dependency_management_tools` → `add_dev_package` | Dev dependency |
| `uv sync` | `install_python_packages` | Install from lock file |
| `uv run <tool>` | `run_tool` | Run Python CLI tool via uvx |
| `uv tool install <tool>` | `install_tool` | Install global CLI tool |
| `uv venv` | `activate_python_environment_management_tools` → `create_venv` | Create virtual env |
| `python --version` | `activate_python_environment_tools` → `get_python_environment_details` | Env info |
| `uv lock` | `generate_lock` | Generate uv.lock |

**Always call `configure_python_environment` before any Python-related tool.**

### Marimo — use `mcp_marimo_*` tools

| Shell command | MCP tool | Notes |
|---|---|---|
| `marimo check app.py` | `mcp_marimo_lint_notebook` | Lint notebook |
| Manual error inspection | `mcp_marimo_get_notebook_errors` | Runtime errors by cell |
| Cell output reading | activate `cell_output_analysis_tools` → `mcp_marimo_get_cell_outputs` | Cell outputs |
| Cell navigation | `mcp_marimo_get_lightweight_cell_map` | Cell structure overview |

### GitHub — use `mcp_github_*` tools

| Shell command | MCP tool | Notes |
|---|---|---|
| `gh pr create` | activate `repository_management_tools` → `create_pull_request` | Create PR |
| `gh issue create` | activate `repository_information_tools` → create issue tools | Create issue |
| `git push` | `mcp_jj_git-push` (via jj) or `run_in_terminal` | Push changes |

## Decision Checklist

Before running a shell command, ask:

1. **Is there a directly available MCP tool?** → Use it.
2. **Is there an activatable tool group?** → Call `activate_*_tools`, then use the unlocked tool.
3. **Does a built-in VS Code tool cover this?** (e.g., `runTests` for pytest) → Use it.
4. **None of the above?** → Fall back to `run_in_terminal`.

## When Shell Commands Are Still Appropriate

- **Exploratory commands** with complex pipes or filters (e.g., `jj log --limit 5 -T ...` with custom templates)
- **Commands with no MCP equivalent** (e.g., `d2 render`, `ruff check --fix`)
- **Chained multi-step operations** where MCP tools would require many sequential calls with no benefit
- **Reading command output** when `run_in_terminal` gives better visibility than an MCP tool's structured response

## Anti-Patterns

### ❌ Bad: Shell when MCP exists

```
run_in_terminal: jj describe -m "feature: red phase"
```

### ✅ Good: Use MCP tool directly

```
mcp_jj_describe(message="feature: red phase")
```

### ❌ Bad: Shell for tests

```
run_in_terminal: uv run pytest tests/data/test_types.py -v
```

### ✅ Good: Use runTests

```
runTests(files=["tests/data/test_types.py"])
```

### ❌ Bad: Shell for package install

```
run_in_terminal: uv add pandas
```

### ✅ Good: Use dependency tool

```
activate_dependency_management_tools() → add_package(packageName="pandas")
```
