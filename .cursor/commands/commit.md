# Commit (jj): save changes and write change description

Use **Jujutsu (jj)** via the **user-jj** MCP server to inspect the current change and set a good change description (and optionally finalize it).

## Steps

1. **Get current state**  
   Call the jj **status** tool (no required args). Use the workspace root as `cwd` if you need to scope the command. From the output, note:
   - The working-copy commit (often `@`) and its current description
   - Parent(s) and any conflict/divergence
   - Summary of changed files (added, modified, removed)

2. **Understand what changed** (if the description is unclear)  
   Call the jj **diff** tool to compare the working copy to its parent:
   - Omit `from` and `to` to diff against the parent of the working copy, or set `to` to `@` and `from` to the parent (e.g. `@-`).
   - Use `stat: true` for a short summary, or leave default for full diff.
   Use this to write an accurate, specific description.

3. **Draft the change description**  
   Write a **conventional commit** message that matches this repo:
   - **Format:** `type(scope): short description` or `type: short description`
   - **Types** (from `pyproject.toml`): `feat`, `fix`, `docs`, `ci`, `test`, `dash`, `dev`, `deps`, `style`, `refactor`, `perf`, `chore`, `nb`
   - Keep the first line short (≤72 chars). Add a body line only if you need to explain why or how.
   - Examples: `feat: add marimo dashboard`, `fix: correct preset application`, `docs: update dashboard guide`

4. **Save the description in jj**  
   - **To only update the current change’s description** (no new change):  
     Call the jj **describe** tool with `message` set to your drafted description. Omit `revisions` so it targets the working copy (`@`).
   - **To “commit” in the Git sense** (set description and start a new empty change):  
     Call the jj **commit** tool with the same `message`. That updates the current change with that message and creates a new empty change on top.

5. **Confirm**  
   Tell the user what you did: which tool you called (describe vs commit), the message you set, and that they can run `jj status` or `jj log` to verify.

## MCP usage

- **Server:** `user-jj`
- **Tools:** `status`, `diff`, `describe`, `commit`
- Always call the tool with the correct schema (e.g. `describe` and `commit` require `message`). Use `cwd` set to the repo root when relevant.

## User intent

- If the user says “describe” or “message” or “save description”: use **describe** only.
- If the user says “commit” or “save and commit” or “finalize”: use **commit** so the current change is recorded and a new empty change is created.
