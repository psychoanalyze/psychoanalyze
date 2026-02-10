---
description: 'Add a description to the currently checked out revision'
---

# Add Description to Current Revision

Examine the currently checked out revision and add a meaningful commit message based on its changes.

## Available Tools

Use jj MCP tools to examine and update the current revision:
- `mcp_jj_show` - Examine current revision changes and context
- `mcp_jj_diff` - Compare file differences (e.g., current vs. parent)
- `mcp_jj_describe` - Update the current revision's description

## Workflow

1. **Examine the current revision** using `mcp_jj_show` (preferred for full context) or `mcp_jj_diff` to inspect what changes were made

2. **Generate a concise, conventional commit message** based on the changes:
   - Use imperative mood ("Add", "Fix", "Update", not "Added", "Fixed")
   - First line: 50 chars max, summarize the change
   - If needed, add blank line then body with details

3. **Apply the description** using `mcp_jj_describe` with the message (defaults to working-copy revision)

## Commit Message Guidelines

- **feat:** New feature or functionality
- **fix:** Bug fix
- **refactor:** Code restructuring without behavior change
- **docs:** Documentation changes
- **test:** Adding or updating tests
- **chore:** Build, tooling, dependency updates
- **style:** Formatting, whitespace changes

## Example

For a revision that adds a new analysis function:
```
feat: add Weber fraction calculation to analysis module
```

For a revision that fixes a plotting bug:
```
fix: correct axis labels in psychometric curve plot
```

## Notes

- If the current revision already has a description, you may want to review it before updating
- Use conventional commit format for consistency with the rest of the repository
- The first line is most important—keep it clear and concise
