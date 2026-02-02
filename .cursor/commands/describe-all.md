# Describe All: Add descriptions to jj revisions missing them

Use **Jujutsu (jj)** via the **user-jj** MCP server to find all revisions without descriptions and add meaningful commit messages to each.

## Steps

1. **Find revisions without descriptions**  
   Call the jj **log** tool to list recent revisions. From the output, identify revisions that have:
   - Empty or "(no description set)" description
   - Actual changes (not empty commits)
   - Are mutable (not immutable/pushed commits)
   
   Typically focus on revisions matching `@ | ancestors(@, 10) & mine() & ~root()` (recent local changes).

2. **For each revision without a description:**

   a. **Examine the revision's changes**  
      Call the jj **show** tool with `revision` set to that commit ID to see:
      - What files were changed
      - The actual diff content
      - Any existing metadata

   b. **Generate an appropriate commit message**  
      Write a **conventional commit** message based on the changes:
      - **Format:** `type(scope): short description` or `type: short description`
      - **Types:** `feat`, `fix`, `docs`, `ci`, `test`, `dash`, `dev`, `deps`, `style`, `refactor`, `perf`, `chore`, `nb`
      - Keep the first line short (≤72 chars)
      - Use imperative mood ("Add", "Fix", "Update", not "Added", "Fixed")

   c. **Apply the description**  
      Call the jj **describe** tool with:
      - `message`: your drafted description
      - `revisions`: the specific commit ID

3. **Report results**  
   After processing all revisions, summarize:
   - How many revisions were found without descriptions
   - What descriptions were applied to each
   - Any revisions skipped (empty changes, already described, immutable)

## MCP Usage

- **Server:** `user-jj`
- **Tools:** `log`, `show`, `describe`
- Use `cwd` set to the repo root: `/home/nixos/code/psychoanalyze`

## Commit Message Guidelines

- **feat:** New feature or functionality
- **fix:** Bug fix
- **refactor:** Code restructuring without behavior change
- **docs:** Documentation changes
- **test:** Adding or updating tests
- **chore:** Build, tooling, dependency updates
- **style:** Formatting, whitespace changes
- **dash:** Dashboard/app changes
- **nb:** Notebook changes
- **deps:** Dependency updates
- **ci:** CI/CD changes

## Example Output

```
Found 3 revisions without descriptions:

1. abc123: Modified src/psychoanalyze/plot.py
   → Applied: "refactor: extract common axis formatting to helper function"

2. def456: Added tests/test_weber.py
   → Applied: "test: add unit tests for Weber fraction calculation"

3. ghi789: Updated pyproject.toml
   → Applied: "deps: bump pandas to 2.1.0"

All revisions now have descriptions.
```

## Notes

- Only describe mutable revisions (not already pushed/immutable)
- Skip revisions that already have meaningful descriptions
- If a revision has no actual changes, note it but don't describe it
- Process revisions from oldest to newest to maintain logical order
