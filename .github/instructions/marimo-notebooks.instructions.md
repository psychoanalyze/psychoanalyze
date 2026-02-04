---
description: "Marimo notebook workflow using MCP tools"
applyTo: "app.py"
---

# Marimo notebook workflow

When editing marimo notebooks, use the marimo MCP tools to guide changes and validate format. The marimo MCP server must be running (for example: `uv run marimo edit app.py --mcp --no-token`) for these tools to be available.

## Before making changes

- Call `get_marimo_rules` (MCP tool) to load official marimo guidelines and best practices. Use the returned rules and source URL to follow marimo-specific conventions (cell structure, reactivity, `mo.ui` usage, and similar) so edits stay within marimo expectations.

## After making changes

- Call `lint_notebook` (MCP tool) to fetch all marimo lint errors for the notebook and address any reported issues:
  - Breaking (MB001-MB005): unparsable cells, multiple definitions, cycle dependencies, setup-cell dependencies, invalid syntax. Fix before considering the edit done.
  - Runtime (MR001-MR002): self-import, branch-expression. Resolve to avoid runtime problems.
  - Formatting (MF001-MF007): general formatting, empty cells, markdown indentation, and similar. Fix for consistency.

You can also run `marimo check app.py` (and `marimo check app.py --fix` where supported) in the terminal to double-check or auto-fix lint issues.

## Debugging runtime errors

When debugging errors in a running notebook:

1. Get the session ID first: call `get_active_notebooks` with `{ "args": {} }` to retrieve the `session_id` for the notebook. This is required for all other debugging tools.
2. View all errors: call `get_notebook_errors` with `{ "args": { "session_id": "..." } }` to see runtime errors across all cells.
3. Inspect specific cells: call `get_cell_runtime_data` with `{ "args": { "session_id": "...", "cell_id": "..." } }` to see the actual code being executed, runtime errors with tracebacks, and variable values and types.
4. Find cell IDs: cells use short hash IDs (for example, "Hstk", "Vxnm"), not function names. Call `get_lightweight_cell_map` to find cell IDs by preview content.

### Important: stale state

The MCP shows state from the last execution. If you edit the file but the notebook has not re-run the cells:
- Errors and variables will be stale.
- The user must manually refresh or re-run the notebook for changes to take effect.
- Code shown in `get_cell_runtime_data` reflects file changes, but `variables` and `errors` reflect the last run.

### Tool argument format

All MCP tools require arguments wrapped in an `args` object:
```json
{"args": {"session_id": "s_abc123", "cell_id": "Hstk"}}
```
