# TDD Revision Splitting - Quick Reference

## What You Get

I've created a complete system for enforcing TDD discipline and handling revision splits:

### 1. Instructions File (Always Active)
**File:** `.github/instructions/jj-revision-splitting.instructions.md`

- Automatically loaded by Copilot (via `applyTo: '**'`)
- Guides splitting oversized revisions
- Shows d2 diagram update patterns
- Provides detection checklist

### 2. Custom Agent (Optional)
**File:** `.github/agents/tdd-red.agent.md`

- Strict enforcement of one-test-per-cycle
- Proactive violation prevention
- Guided splitting workflow
- Auto-updates d2 diagrams

### 3. Strategy Guide
**File:** `.github/docs/tdd-enforcement-strategy.md`

- Compares agent vs instructions approach
- Phased adoption plan (learning → integration → automation)
- Metrics for measuring TDD discipline
- Migration path recommendations

### 4. Agent Registry
**File:** `.github/AGENTS.md`

- Documents all custom agents
- Usage guidelines and examples
- Agent chaining patterns

## Quick Start

### Option A: Use Instructions Only (Recommended to Start)

Just continue working normally. The instructions are already active. When I detect multiple tests in a revision, I'll guide you through splitting.

**Trigger phrases:**
- "I wrote too many tests"
- "Split this revision"
- "Fix TDD violation"

### Option B: Use Custom Agent (Strict Mode)

Explicitly invoke the agent for red phases:

```
Use the tdd-red agent to write a test for hit rate calculation
```

The agent will:
1. Validate your request is atomic (ONE test only)
2. Write ONE test function
3. Run the test to verify it fails
4. Guide you through commit
5. Detect and split any violations

## Workflow Examples

### ✅ Correct: One Test Per Cycle

```bash
# Red Phase - Cycle 1
jj new -m "trial-agg: red - test grouping by intensity"
# Write ONE test: test_aggregate_groups_by_intensity()
uv run pytest tests/data/test_trials.py::test_aggregate_groups_by_intensity -v
# FAILS ✓
jj commit

# Green Phase - Cycle 1
jj new -m "trial-agg: green - implement grouping"
# Implement minimal code
uv run pytest tests/data/test_trials.py::test_aggregate_groups_by_intensity -v
# PASSES ✓
jj commit

# Red Phase - Cycle 2
jj new -m "trial-agg: red - test hit rate calculation"
# Write ONE test: test_aggregate_calculates_hit_rate()
# ... continue ...
```

### ❌ Violation: Multiple Tests Written

**Detection:**
```bash
jj show @
# + def test_aggregate_groups_by_intensity(): ...
# + def test_aggregate_calculates_hit_rate(): ...  ← VIOLATION!
# + def test_aggregate_handles_empty_dataframe(): ...
```

**Correction:**
```bash
# 1. Abort oversized revision
jj abandon @  # Keeps changes in working copy

# 2. Create atomic revisions
jj new -m "trial-agg-grouping: red - test grouping"
# Edit file: keep ONLY test_aggregate_groups_by_intensity
jj commit

jj new -m "trial-agg-grouping: green - implement grouping"
# Implement
jj commit

jj new -m "trial-agg-hit-rate: red - test hit rate"
# Edit file: add test_aggregate_calculates_hit_rate
jj commit
# ... continue for all tests ...

# 3. Update d2 diagram
# Edit docs/plan.d2
# Replace:
#   trial_aggregation: "trials → points"
# With:
#   trial_aggregation_grouping: "trials: grouping"
#   trial_aggregation_hit_rate: "trials: hit rate"
#   trial_aggregation_edge_cases: "trials: edge cases"
#
#   trial_aggregation_grouping -> trial_aggregation_hit_rate -> trial_aggregation_edge_cases

d2 docs/plan.d2 docs/figures/plan.svg
```

## D2 Diagram Updates

### Pattern: Linear Dependency Chain

```d2
# Before split
feature: "feature implementation"
parent -> feature -> next

# After split
feature_a: "feature: behavior A"
feature_b: "feature: behavior B"
feature_c: "feature: behavior C"

parent -> feature_a -> feature_b -> feature_c -> next
```

### Pattern: Parallel Independent Behaviors

```d2
# Before split
feature: "feature implementation"

# After split
feature_core: "feature: core"
feature_validation: "feature: validation"
feature_output: "feature: output"

parent -> feature_core -> next
parent -> feature_validation -> next
parent -> feature_output -> next
```

## Cheat Sheet

### Detection
```bash
# Count tests in current revision
jj diff -r @ | grep -c "^+def test_"

# Show tests added
jj diff -r @ | grep "^+def test_"

# View full revision
jj show @
```

### Splitting
```bash
# Abandon current revision (keeps changes in working copy)
jj abandon @

# Create new atomic revision
jj new -m "<feature>: red - <one-behavior>"

# Edit test file (keep only one test)
vim tests/data/test_trials.py

# Verify single test
grep -c "^def test_" tests/data/test_trials.py  # Should be 1

# Run test
uv run pytest tests/data/test_trials.py -v

# Commit
jj commit
```

### Absorb (Fix without new revisions)
```bash
# Fix test in working copy after committing
vim tests/data/test_trials.py
uv run pytest tests/data/test_trials.py -v  # Verify fix

# Absorb into red phase instead of new revision
jj absorb -r @-  # Absorb into parent revision

# Absorb into current revision
jj absorb -r @

# Absorb into older revision (go back N steps)
jj absorb -r @--   # 2 revisions back
jj absorb -r @---  # 3 revisions back

# Preview what will be absorbed before committing
jj diff -r @:@-

# View how a revision evolved (with diffs between versions)
jj evolog -p @

# Compare two versions of same revision (interdiff)
jj interdiff --from <old-id> --to <new-id>
```

### When to Use Absorb vs Splitting

| Situation                       | Absorb | Split |
| ------------------------------- | ------ | ----- |
| Test syntax fix after commit    | ✅      |       |
| Missing import stub             | ✅      |       |
| Test assertion refinement       | ✅      |       |
| Multiple test functions         |        | ✅     |
| Different behaviors in one test |        | ✅     |
| Type annotation fix             | ✅      |       |
| Block-scoped test edit          | ✅      |       |

### D2 Updates
```bash
# Edit plan
vim docs/plan.d2

# Validate syntax by rendering
d2 docs/plan.d2 docs/figures/plan.svg

# Check output
ls -lh docs/figures/plan.svg

# View (optional)
xdg-open docs/figures/plan.svg
```

## Validation Checklist

After splitting revisions:

- [ ] Each red phase revision has exactly 1 test function
- [ ] Each test tests exactly 1 behavior
- [ ] All tests run and fail/pass as expected
- [ ] `jj log` shows clear red/green/refactor pattern
- [ ] D2 diagram updated with atomic nodes
- [ ] D2 diagram renders without errors
- [ ] All nodes have clear, concise labels
- [ ] Dependencies between nodes are correct
- [ ] `jj evolog -p @` shows clean revision evolution (no diff soup)

## Measuring TDD Discipline

Track your progress:

```nushell
# Violation rate (target: <5%)
jj log --limit 50
| grep "red phase"
| each {|line|
    let rev = ($line | parse "{id} {rest}" | get id.0)
    let count = (jj diff -r $rev | grep "^+def test_" | lines | length)
    {revision: $rev, tests: $count, violation: ($count > 1)}
}
| where violation == true
| length
```

## Recommended Approach

### Week 1-2: Learn with Instructions
- Continue normal workflow
- Let instructions guide corrections
- Manually split when violations occur
- Track violation frequency

### Week 3-4: Evaluate Need for Agent
- If violation rate >20%: Use custom agent
- If violation rate <10%: Continue with instructions
- If violations complex: Consider automation

### Month 2+: Optimize
- Add pre-commit hooks if desired
- Refine d2 diagram patterns
- Share learnings with team

## Getting Help

### From Instructions
```
"Split this revision - I wrote multiple tests"
"How do I handle multiple tests in one revision?"
"Update d2 diagram after revision split"
```

### From Agent
```
"Use the tdd-red agent to write a test for [behavior]"
"tdd-red: split this oversized revision"
"tdd-red: update d2 diagrams"
```

### From Other Agents
```
"Use jj-helper to rebase these split revisions"
"Use marimo-helper to update dashboard after data pipeline changes"
```

## Resources

- **Full Splitting Guide:** `.github/instructions/jj-revision-splitting.instructions.md`
- **Agent Documentation:** `.github/agents/tdd-red.agent.md`
- **Strategy & Metrics:** `.github/docs/tdd-enforcement-strategy.md`
- **JJ TDD Workflow:** `.github/skills/jj-tdd-revisions/SKILL.md`
- **All Agents:** `.github/AGENTS.md`

## Next Steps

1. ✅ Files created and ready to use
2. Read `.github/docs/tdd-enforcement-strategy.md` for detailed decision framework
3. Continue your current work - instructions are already active
4. If you detect a violation, just say "split this revision"
5. After 2 weeks, review violation rate and decide if you want strict agent enforcement

---

**Remember:** Slow is smooth. Smooth is fast. One test at a time. 🎯
