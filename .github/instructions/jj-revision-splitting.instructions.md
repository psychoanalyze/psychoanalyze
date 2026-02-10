---
description: 'Instructions for splitting oversized jj revisions that violate TDD discipline and updating d2 diagrams to reflect the corrected workflow. Use when a revision contains multiple tests instead of following one-test-per-cycle discipline.'
applyTo: '**'
---

# JJ Revision Splitting for TDD Discipline

## Core Principle

**STRICT TDD DISCIPLINE: One test per Red→Green→Refactor cycle.**

Each jj revision should represent ONE complete TDD cycle:
- **Red**: Write ONE failing test describing ONE behavior (you may write type stubs/function signatures so tests can import and run, but no implementation logic)
- **Green**: Implement minimal code to make THAT ONE test pass
- **Refactor**: Improve code quality while keeping THAT ONE test green

**Red Phase Goal:** See a failing **assertion** (e.g., `AssertionError: expected 0.5, got None`), not a runtime error (e.g., `NameError: 'aggregate' not defined`).

## Why Clean History Matters

Each revision is a **logically separated, independently readable unit of change**. This matters because:

1. **`jj log` / `git blame` accuracy** — When every revision has one clear purpose, blame points to meaningful changes, not "fix review" noise.
2. **`git bisect` reliability** — Clean atomic revisions make bisection land on the actual root cause, not an ambiguous fixup commit.
3. **Interdiff review** — When revisions need updating (review feedback, bug fixes), we update the original revision in-place (via `jj absorb`, `jj squash`, or `jj edit`) rather than appending fixup commits on top. This avoids "diff soup" — a pile of follow-up commits with unclear relationships to the originals.
4. **Reviewability** — Reviewers can use `jj evolog` to see how a revision evolved across versions, and `jj interdiff` to see only what changed between iterations.

**Anti-pattern: "diff soup"** — Appending commits like "fix review", "address feedback", "minor tweak" on top of the original series. This destroys blame/bisect signal and forces reviewers to re-read everything.

**Correct pattern: versioned revisions** — Update the original revision in-place. JJ makes this natural because revisions are mutable. Use `jj absorb` for surgical updates, `jj squash` for folding changes, and `jj edit` for direct modification.

## When to Use This Workflow

Use this workflow when you detect you've violated TDD discipline by:
- Writing multiple test functions in one red phase
- Writing multiple assertions testing different behaviors in one test
- Implementing multiple features in one green phase
- Creating a revision that's too large to describe in one sentence

## Detection Patterns

### ❌ Bad: Multiple Tests in One Revision

```python
# In tests/data/test_trials.py - RED PHASE
def test_aggregate_groups_by_intensity():
    """Should group trials by intensity level."""
    # ... test code ...

def test_aggregate_calculates_hit_rate():
    """Should calculate hit rate as hits/total."""
    # ... test code ...

def test_aggregate_handles_empty_dataframe():
    """Should return empty DataFrame when input is empty."""
    # ... test code ...
```

**Problem**: Three different behaviors tested in one revision → violates one-test-per-cycle.

### ✅ Good: One Test Per Revision

**Revision 1: trial-aggregation-grouping**
```python
def test_aggregate_groups_by_intensity():
    """Should group trials by intensity level."""
    # ... ONE test for ONE behavior ...
```

**Revision 2: trial-aggregation-hit-rate** (based on revision 1)
```python
def test_aggregate_calculates_hit_rate():
    """Should calculate hit rate as hits/total."""
    # ... ONE test for ONE behavior ...
```

**Revision 3: trial-aggregation-edge-cases** (based on revision 2)
```python
def test_aggregate_handles_empty_dataframe():
    """Should return empty DataFrame when input is empty."""
    # ... ONE test for ONE behavior ...
```

## Splitting Workflow

### Step 1: Identify the Oversized Revision

Run `jj log` and identify the revision with multiple tests:

```bash
jj log
# @ qpvuntsq ty@ty.com 2026-02-06 15:23:45 trial-aggregation
# │ trial-aggregation: red phase - write failing tests
# │ FILES: tests/data/test_trials.py (3 test functions) ❌ TOO MANY!
```

### Step 2: List the Individual Behaviors

Extract each distinct behavior being tested:

1. Group trials by intensity level
2. Calculate hit rate as hits/total
3. Handle empty DataFrame edge case

Each behavior = one future revision.

### Step 3: Abandon the Oversized Revision

```bash
# Move back to parent revision (before the oversized one)
jj edit <parent-revision-id>

# Abandon the oversized revision
jj abandon <oversized-revision-id>
```

### Step 4: Create Atomic Revisions

For each behavior identified in Step 2, create a new revision following strict TDD:

**First revision:**
```bash
jj new -m "trial-aggregation-grouping: red phase - test grouping by intensity"
# Write ONLY test_aggregate_groups_by_intensity
uv run pytest tests/data/test_trials.py::test_aggregate_groups_by_intensity -v
# Test should FAIL (red)
jj commit

jj new -m "trial-aggregation-grouping: green phase - implement grouping"
# Implement minimal code to pass the test
uv run pytest tests/data/test_trials.py::test_aggregate_groups_by_intensity -v
# Test should PASS (green)
jj commit

jj new -m "trial-aggregation-grouping: refactor - improve types/docs"
# Refactor while keeping test green
jj commit
```

**Second revision (building on first):**
```bash
jj new -m "trial-aggregation-hit-rate: red phase - test hit rate calculation"
# Write ONLY test_aggregate_calculates_hit_rate
# ... repeat red/green/refactor ...
```

**Continue for each behavior...**

### Step 5: Update D2 Diagrams

After splitting revisions, update the relevant d2 diagrams to reflect the finer-grained structure.

#### Before Splitting (docs/plan.d2)
```d2
data_schema -> trial_aggregation
trial_aggregation -> contract_validation
```

#### After Splitting (docs/plan.d2)
```d2
data_schema -> trial_aggregation_grouping
trial_aggregation_grouping -> trial_aggregation_hit_rate
trial_aggregation_hit_rate -> trial_aggregation_edge_cases
trial_aggregation_edge_cases -> contract_validation
```

**Update procedure:**
1. Open the d2 file: `docs/plan.d2`
2. Locate the oversized revision node in the `jj_planning` section
3. Replace the single node with a chain of atomic nodes
4. Update edge connections to reflect dependencies
5. Keep labels concise but descriptive (4-6 words max)
6. Verify with: `d2 docs/plan.d2 docs/figures/plan.svg`

## D2 Diagram Update Patterns

### Pattern 1: Linear Chain

When behaviors must be implemented sequentially:

```d2
# Before
feature: "feature implementation"

# After
feature_step1: "feature: core logic"
feature_step2: "feature: edge cases"
feature_step3: "feature: error handling"

feature_step1 -> feature_step2 -> feature_step3
```

### Pattern 2: Parallel Branches

When behaviors can be implemented independently:

```d2
# Before
feature: "feature implementation"

# After
feature_core: "feature: core logic"
feature_validation: "feature: input validation"
feature_output: "feature: output formatting"

parent -> feature_core
parent -> feature_validation
parent -> feature_output

feature_core -> next_step
feature_validation -> next_step
feature_output -> next_step
```

### Pattern 3: Incremental Enhancement

When adding progressively complex behaviors:

```d2
# Before
model_fitting: "model fitting"

# After
model_basic: "model: simple fit"
model_bounds: "model: add constraints"
model_regularization: "model: add L2 penalty"
model_bootstrap: "model: add CI via bootstrap"

model_basic -> model_bounds -> model_regularization -> model_bootstrap
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Writing Tests for Different Functions

```python
def test_aggregate_returns_dataframe():
    result = aggregate(trials_df)
    assert isinstance(result, pd.DataFrame)

def test_fit_returns_threshold():  # ❌ Different function!
    params = fit(points_df)
    assert "x0" in params.columns
```

**Fix**: These belong in different revisions AND different test files.

### ❌ Mistake 2: Testing Truly Different Behaviors in One Test

```python
def test_aggregate():
    result = aggregate(trials_df)
    assert isinstance(result, pd.DataFrame)  # Hierarchical assertion
    assert "Hit Rate" in result.columns      # Hierarchical assertion
    assert result["Hit Rate"].max() <= 1.0   # Hierarchical assertion

    # ❌ DIFFERENT behavior - should be separate test!
    assert "n trials" in result.columns
    assert result.groupby("Intensity").size().min() >= 1
```

**Important distinction:**
- **Hierarchical assertions** (checking type → structure → bounds) can be **combined** in one test - each builds on the previous
- **Different behaviors** (hit rate calculation vs. grouping logic) **must be split** into separate tests

**Fix for hierarchical assertions** - This is actually OK:
```python
def test_aggregate_calculates_hit_rate():
    """Hit rate should be between 0 and 1 with correct column structure."""
    result = aggregate(trials_df)
    assert isinstance(result, pd.DataFrame)  # Prerequisite check
    assert "Hit Rate" in result.columns      # Structure check
    assert result["Hit Rate"].max() <= 1.0   # Bounds check
    assert result["Hit Rate"].min() >= 0.0   # (combined with bounds)
```

**Fix for different behaviors** - Split these:
```python
# Test 1: Hit rate calculation
def test_aggregate_calculates_hit_rate():
    result = aggregate(trials_df)
    assert "Hit Rate" in result.columns
    assert (result["Hit Rate"] >= 0).all() and (result["Hit Rate"] <= 1).all()

# Test 2: Grouping by intensity (DIFFERENT behavior)
def test_aggregate_groups_by_intensity():
    result = aggregate(trials_df)
    assert result.index.name == "Intensity"
    assert len(result) == trials_df["Intensity"].nunique()
```

**Gold standard:** Use property-based testing with Hypothesis or Polars testing:
```python
from hypothesis import given
from hypothesis.extra.pandas import data_frames, column

@given(data_frames([
    column("Intensity", dtype=int),
    column("Result", dtype=int),
]))
def test_aggregate_properties(trials_df):
    """Hit rate should always be between 0 and 1 for any valid input."""
    result = aggregate(trials_df)
    assert (result["Hit Rate"] >= 0).all()
    assert (result["Hit Rate"] <= 1).all()
```

Property-based tests can combine many assertions because they test **invariants** that should hold for all inputs. Start with narrower assertions, refactor to property-based tests when the pattern becomes clear.

### ❌ Mistake 3: Premature Abstraction

```python
# RED PHASE - writing test for "calculate hit rate"
# ❌ DON'T implement helper functions yet!
def _calculate_rate(hits, total):
    return hits / total  # This is LOGIC, not a stub!

def test_aggregate_calculates_hit_rate():
    # ...
```

**Fix**: Write failing test first. Extract helpers in REFACTOR phase.

**Note**: Function stubs are OK to avoid import errors:
```python
# ✅ OK in red phase (stub with no logic)
def aggregate(trials_df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame()  # or raise NotImplementedError
```

## Checklist for Proper Revision Splitting

Before committing a red phase, verify:

- [ ] There is exactly ONE test function
- [ ] The test asserts exactly ONE behavior (hierarchical assertions like type → structure → bounds are OK)
- [ ] The test can be described in one sentence
- [ ] The jj commit message matches that sentence
- [ ] Running the test produces ONE clear **assertion** failure (not NameError/ImportError)
- [ ] No implementation logic exists yet (type stubs/function signatures OK, but no actual logic)

Before updating d2 diagrams, verify:

- [ ] Each new node represents one complete red/green/refactor cycle
- [ ] Node labels describe the behavior, not the test name
- [ ] Dependencies between nodes are accurate
- [ ] The overall graph structure matches the jj revision tree
- [ ] Rendering the d2 file produces a valid SVG

## Integration with jj-helper Agent

For complex revision surgery (reordering, squashing, rebasing), delegate to the **jj-helper** subagent:

```
Use jj-helper when:
- Splitting requires reordering multiple revisions
- You need to preserve commit metadata during splits
- Handling conflicts during revision reorganization
- Analyzing revision evolution with `jj evolog`
```

## Using JJ Absorb for Revision Updates

JJ's `absorb` feature is an elegant alternative to creating new revisions for small changes. Instead of "fix typo" commits, absorb changes into the appropriate earlier revision.

### Absorb in Red Phase

**Fix test after committing:**
```bash
jj new -m "feature: red - test behavior"
# Write test
jj commit

# Realize test has syntax error or needs refinement
vim tests/data/test_trials.py
uv run pytest tests/data/test_trials.py -v  # Verify fix

# Absorb fix into red phase (don't create new revision)
jj absorb -r @-

# Continue to green phase
jj new -m "feature: green - implement"
```

### Absorb Across Phases

**Type stub needed for imports (green phase adding to red):**
```bash
# Red phase written, green phase in progress
jj new -m "feature: green - implement"

# Realize: test imports type that doesn't exist yet
vim src/psychoanalyze/data/trials.py
# Add stub only: def aggregate(trials_df: pd.DataFrame) -> pd.DataFrame: ...

# Absorb stub into red phase (not green)
jj absorb -r @--  # Go back 2 revisions to red

# Now continue green phase implementation
```

### When to Absorb vs Split

**Use absorb for:**
- Small refinements to existing revisions
- Type stubs needed for imports
- Test assertion improvements
- Documentation fixes
- Variable name consistency

**Use splitting for:**
- Adding truly separate test functions
- Multiple independent behaviors
- Features that can't fit under one assertion

### Absorb Patterns for TDD

| Situation | Action | Result |
|-----------|--------|--------|
| Test syntax error after commit | `jj absorb -r @-` | Fix in red phase, no new commit |
| Need import stub | `jj absorb -r @` | Stub in current revision |
| Improve assertion message | `jj absorb -r @--` | Better assertion in red phase |
| Add type annotation | `jj absorb -r <rev>` | Type added to target revision |
| Fix docstring | `jj absorb -r @` | Docs improved in current revision |

### Absorb Command Reference

```bash
# Absorb working copy into current revision
jj absorb -r @

# Absorb into parent (previous revision)
jj absorb -r @-

# Absorb into grandparent
jj absorb -r @--

# Absorb into specific revision (by hash)
jj absorb -r abc1234def

# Preview what will be absorbed
jj diff -r @:@-
```

### Absorb Benefits

✅ **Preserves metadata** - Commit date, author, message stay on original revision (unlike squash)

✅ **Clean history** - No "fix typo" commits cluttering the log

✅ **TDD-friendly** - Refactor revisions without creating new ones

✅ **Atomic revisions** - Keeps red/green/refactor phases truly atomic

⚠️ **Can only absorb backward** - Into earlier (ancestor) revisions only

## Reviewing Revision Evolution

JJ tracks how each revision evolves over time. This is the "interdiff" equivalent — you can see what changed between version 1 and version 2 of a revision without re-reading the whole thing.

### Using `jj evolog` for Review

```bash
# See how the current revision has been updated over time
jj evolog @

# See evolution with diffs between each version
jj evolog -p @

# See evolution of a specific earlier revision
jj evolog -p @-
```

This is essential after absorbing changes — `evolog` proves what was modified without re-reading the entire revision.

### Using `jj interdiff` for Pairwise Comparison

```bash
# Compare two versions of a revision (from evolog output)
jj interdiff --from <old-commit-id> --to <new-commit-id>
```

This shows only the delta between two versions of the same revision — the "interdiff" that makes code review incremental rather than exhaustive.

### Why This Matters for TDD

Each red/green/refactor cycle is like a patch in a series:
- **Red phase** = Patch 1 (test)
- **Green phase** = Patch 2 (implementation)
- **Refactor phase** = Patch 3 (cleanup)

When you absorb a fix into red phase, reviewers don't re-read the whole test — they run `jj evolog -p @` and see only the 2-line fix. This is the interdiff advantage.

## Quick Reference Commands

```bash
# View revision history
jj log --limit 10

# Show details of current revision
jj show @

# See what's in a revision
jj file-list -r @

# Abandon current revision (keep changes in working copy)
jj abandon @

# Edit a different revision
jj edit <revision-id>

# Create new revision based on current
jj new -m "description"

# View evolution of a revision
jj evolog @

# Rebase revision onto new parent
jj rebase -s <source> -d <destination>
```

## Validation

After splitting and updating diagrams, validate the workflow:

```bash
# 1. Verify jj revision structure
jj log --limit 20
# Should show: red → green → refactor → red → green → refactor ...

# 2. Verify each revision has one test
for rev in $(jj log --no-graph --limit 10 | grep "red phase"); do
    jj show $rev | grep "def test_" | wc -l  # Should output: 1
done

# 3. Verify d2 diagram renders
d2 docs/plan.d2 docs/figures/plan.svg

# 4. Run full test suite
uv run pytest tests/ -v
```

## Summary

**Golden Rule**: One test, one behavior, one revision, one cycle.

**Interdiff mindset**: Update revisions in-place, don't append fixups. Clean history makes blame, bisect, and review work.

When you catch yourself writing multiple tests:
1. **Stop** immediately
2. **Identify** distinct behaviors
3. **Abandon** the oversized revision
4. **Create** atomic revisions (one per behavior)
5. **Update** d2 diagrams to reflect new structure
6. **Validate** with jj log and pytest

This discipline keeps your revision history clean, your tests focused, and your workflow reviewable.
