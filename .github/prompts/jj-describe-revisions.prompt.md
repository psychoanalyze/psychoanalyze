---
description: 'Add descriptions to jj revisions that lack them'
---

# Add Descriptions to Undescribed Revisions

Find all revisions without descriptions and add meaningful commit messages based on their changes.

## Available Tools

**Preferred:** Use jj MCP tools when available. They provide structured output and direct integration:
- `mcp_jj_log` - List revisions
- `mcp_jj_show` - Examine revision changes
- `mcp_jj_diff` - Compare file differences
- `mcp_jj_describe` - Update revision descriptions

**Fallback:** Use CLI commands (`jj log`, `jj show`, `jj describe`) if MCP tools are unavailable.

## Workflow

1. **List undescribed revisions** using `mcp_jj_log` to identify those with "(no description set)"

2. **Examine each undescribed revision** using `mcp_jj_show` (preferred for context) or `mcp_jj_diff` to inspect what changes were made

3. **Generate a concise, conventional commit message** based on the changes:
   - Use imperative mood ("Add", "Fix", "Update", not "Added", "Fixed")
   - First line: 50 chars max, summarize the change
   - If needed, add blank line then body with details

4. **Apply the description** using `mcp_jj_describe` with the revision ID and message

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

- Skip the root/empty revision (usually marked with "(empty)")
- Skip revisions that already have descriptions
- Work from oldest to newest to maintain logical history
- Ask for confirmation before applying descriptions if many changes
