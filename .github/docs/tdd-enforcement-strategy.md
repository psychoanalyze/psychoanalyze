# TDD Enforcement Strategy: Agent vs Instructions

## The Problem

You're following strict TDD discipline with jj revisions, but occasionally violate the "one test per cycle" rule. When this happens, you need to:

1. **Detect** the violation (multiple tests in one revision)
2. **Split** the revision into atomic cycles
3. **Update** d2 diagrams to reflect the corrected structure
4. **Learn** to avoid repeating the mistake

### Why Clean History Matters

Clean atomic revisions aren't just aesthetic — they enable:
- **`git blame` accuracy** — Each revision has one clear purpose
- **`git bisect` reliability** — Bisection lands on the actual root cause
- **Interdiff review** — Update revisions in-place (via `jj absorb`/`jj edit`) instead of appending "fix review" commits. Reviewers use `jj evolog` and `jj interdiff` to see only what changed between iterations.

The alternative — appending fixup commits ("diff soup") — destroys blame/bisect signal and forces reviewers to re-read everything.

## Solution Options

### Option 1: Custom TDD-Red Agent (Recommended for Phase 1)

**Create:** `.github/agents/tdd-red.agent.md`

```yaml
---
name: tdd-red
description: Enforces strict one-test-per-cycle TDD discipline during red phases. Prevents writing multiple tests, validates test atomicity, and guides revision splitting when violations occur.
toolRestrictions:
  - name: edit_notebook_file
    restriction: blocked
  - name: run_in_terminal
    restriction: allowed
  - name: replace_string_in_file
    restriction: allowed
---

# TDD Red Phase Agent

## Role

You are a strict TDD enforcer specializing in red phases. Your job is to ensure ONE test per cycle and help split violations.

## Constraints

YOU MUST:
- Write exactly ONE test function per invocation
- Test exactly ONE behavior per function
- Fail with clear error message if user requests multiple tests
- Validate atomicity before committing
- Guide revision splitting when violations detected

YOU MUST NOT:
- Write implementation code (that's green phase)
- Write multiple test functions in one pass
- Combine multiple behaviors in one test
- Skip validation checks

## Workflow

1. **Analyze Request**: What ONE behavior needs testing?
2. **Validate Atomicity**: Can this be described in one sentence?
3. **Write Test**: Create ONE test function with ONE assertion
4. **Verify Failure**: Run test, confirm it fails for right reason
5. **Commit**: `jj commit -m "<feature>: red phase - <one-sentence-description>"`

## Detection & Splitting

If you detect multiple tests already written:

1. Count test functions: `grep -c "^def test_" <file>`
2. If count > 1, STOP and initiate splitting workflow
3. Use jj-revision-splitting.instructions.md
4. Update d2 diagrams in docs/

## Examples

### ✅ Valid Request
**User**: "Write test for hit rate calculation"
**Action**: Write `test_aggregate_calculates_hit_rate()` (ONE test)

### ❌ Invalid Request
**User**: "Write tests for hit rate, edge cases, and empty DataFrame"
**Response**:
```
❌ TDD Discipline Violation Prevented

You requested 3 tests in one cycle:
1. hit rate calculation
2. edge cases
3. empty DataFrame handling

I can only write ONE test per red phase. Which ONE behavior should I test first?

Recommended order:
1. trial-aggregation-hit-rate-red
2. trial-aggregation-edge-cases-red
3. trial-aggregation-empty-red
```

### 🔧 Split Oversized Revision
**Detection**: Found 3 test functions in `tests/data/test_trials.py`
**Action**:
1. Run splitting workflow from jj-revision-splitting.instructions.md
2. Create 3 atomic revisions
3. Update `docs/plan.d2`:
   ```d2
   trial_aggregation_step1 -> trial_aggregation_step2 -> trial_aggregation_step3
   ```
```

**Pros:**
- ✅ Proactive enforcement (prevents violations)
- ✅ Automatic detection of violations
- ✅ Guided splitting workflow
- ✅ Contextual to TDD phase
- ✅ Reusable across all features

**Cons:**
- ❌ Requires explicit agent invocation ("use tdd-red agent")
- ❌ Context switching between agents (red/green/refactor)
- ❌ May be overly strict for exploratory phases

**Best For:**
- Early phases of TDD adoption
- Training yourself on discipline
- Complex features with many edge cases
- When working under time pressure (easy to slip)

### Option 2: Instructions-Based Learning (Recommended for Phase 2)

**Keep:** `.github/instructions/jj-revision-splitting.instructions.md` (already created)

**How it works:**
- Copilot reads instructions automatically via `applyTo: '**'`
- No agent invocation needed
- Learns patterns from your corrections
- Becomes embedded in general workflow

**Pros:**
- ✅ Always active (no invocation needed)
- ✅ Seamless integration with normal flow
- ✅ Less context switching
- ✅ Learns from repeated corrections

**Cons:**
- ❌ Reactive, not proactive (catches after violation)
- ❌ Relies on you to notice violations
- ❌ May not enforce as strictly

**Best For:**
- After you've internalized TDD discipline
- When you want minimal friction
- Long-term sustainable workflow

### Option 3: Automated Rule Enforcement (Future)

Use pre-commit hooks and CI checks:

**File:** `.github/hooks/pre-commit-tdd-check.nu`

```nushell
#!/usr/bin/env nu

# Check if current revision is a red phase
let commit_msg = (jj log --limit 1 --no-graph | lines | first)

if ($commit_msg | str contains "red phase") {
    # Count test functions added in this revision
    let test_count = (
        jj diff | grep "^+def test_" | lines | length
    )

    if $test_count > 1 {
        print $"❌ TDD Violation: ($test_count) tests in one red phase"
        print "Rule: ONE test per red phase"
        print ""
        print "See: .github/instructions/jj-revision-splitting.instructions.md"
        exit 1
    }

    print $"✅ TDD Check: ($test_count) test (valid)"
}
```

**Pros:**
- ✅ Fully automated enforcement
- ✅ Catches violations before commit
- ✅ No human oversight needed
- ✅ Embeds in team workflow

**Cons:**
- ❌ Requires hook setup
- ❌ May be too rigid for exceptions
- ❌ Needs maintenance

## Recommended Strategy

### Phase 1: Learning (Weeks 1-4)
**Use:** Custom TDD-Red Agent

Explicitly invoke the agent for every red phase:
```
Use the tdd-red agent to write a test for hit rate calculation
```

This trains both you and Copilot on the discipline through forced adherence.

### Phase 2: Integration (Weeks 5-12)
**Use:** Instructions-Based Learning

Stop invoking the agent. Let instructions file guide corrections:
- Copilot catches violations from instructions
- You reinforce by splitting when caught
- Pattern recognition improves over time

### Phase 3: Automation (Long-term)
**Use:** Pre-commit Hooks

Implement automated checks:
- Hook validates before commit
- CI validates before merge
- Zero friction, zero violations

## Migration Path

### Week 1-2: Create & Use Agent
```bash
# Create agent
vim .github/agents/tdd-red.agent.md

# Use it explicitly
"Use tdd-red agent to write test for..."
```

### Week 3-6: Monitor Effectiveness
```bash
# Track violation rate
jj log --limit 50 | grep "red phase" | while { ... }
# Count: revisions with >1 test / total red revisions
```

### Week 7+: Transition to Instructions
```bash
# Stop invoking agent
# Let instructions catch violations
# Reinforce through manual splitting
```

### Month 3+: Add Automation
```bash
# Install hook
cp .github/hooks/pre-commit-tdd-check.nu .jj/hooks/
chmod +x .jj/hooks/pre-commit-tdd-check.nu

# Test it
echo "test violation" | jj commit  # Should fail
```

## Advanced: Using JJ Absorb for Clean TDD

Beyond basic splitting, jj's `absorb` feature makes TDD even cleaner:

### How Absorb Improves TDD

**Traditional Flow (with extra commits):**
```
red phase ✓
green phase ✓
fix red phase bug → NEW COMMIT (unmaintainable)
refactor green phase → NEW COMMIT (cluttered history)
```

**With Absorb (clean history):**
```
red phase ✓
green phase ✓
fix red phase bug & `jj absorb -r @--` → ABSORBED (clean)
refactor & `jj absorb -r @-` → ABSORBED (clean)
```

### Patterns for Each Phase

**Red Phase:**
```bash
jj new -m "feature: red - test X"
# Write test & commit

# Realize test needs refinement
vim tests/...
jj absorb -r @  # Into red phase, not new commit
```

**Green Phase:**
```bash
jj new -m "feature: green - implement X"
# Write implementation

# Discover: assertion was too weak, fix it
vim tests/...
jj absorb -r @-  # Back into red phase

# Now continue green with stronger requirement
```

**Refactor Phase:**
```bash
jj new -m "feature: refactor - improve X"
# Clean up code

# Find: we missed a type annotation
vim src/...
jj absorb -r @  # Into refactor phase
```

### Absorb in Practice

Real-world TDD with absorb typically looks like:

1. **Red Phase** → Write test, commit
2. **Discover test refinement needed** → Fix & `jj absorb -r @-`
3. **Green Phase** → Implement, commit
4. **Type annotation missing** → Add stub & `jj absorb -r @--` (back to red)
5. **Refactor Phase** → Improve code, commit
6. **Docstring improvement** → Fix & `jj absorb -r @` (into refactor)

This keeps your revision history clean while allowing you to be creative and discovery-driven.

### Reviewing Changes with Interdiff

After absorbing changes, verify what was modified without re-reading entire revisions:

```bash
# See how a revision evolved over time (with diffs)
jj evolog -p @

# Compare two versions of the same revision
jj interdiff --from <old-commit-id> --to <new-commit-id>
```

This is the interdiff advantage — reviewers see only the delta between revision versions, not the entire patch re-read.

## Measuring Success

Track these metrics:

```nushell
# Violation rate (target: <5%)
def tdd-violation-rate [] {
    let red_phases = (jj log --limit 100 | grep "red phase" | lines | length)
    let violations = (
        jj log --limit 100
        | grep "red phase"
        | each { |line|
            let rev_id = ($line | parse "{id} {rest}" | get id.0)
            let test_count = (jj diff -r $rev_id | grep "^+def test_" | lines | length)
            if $test_count > 1 { 1 } else { 0 }
        }
        | math sum
    )

    $violations / $red_phases * 100
}

# Average tests per red phase (target: 1.0)
def avg-tests-per-red [] {
    jj log --limit 100
    | grep "red phase"
    | each { |line|
        jj diff -r (parse ...) | grep "^+def test_" | lines | length
    }
    | math avg
}

# Time to split (how long to notice violation) (target: <5 min)
# Manual tracking in first few weeks
```

## Decision Framework

**Choose Custom Agent if:**
- [ ] You violate TDD discipline >20% of time
- [ ] You're new to strict TDD
- [ ] You're working on complex features
- [ ] You want proactive enforcement

**Choose Instructions Only if:**
- [ ] You violate TDD discipline <10% of time
- [ ] You're experienced with TDD
- [ ] You want minimal friction
- [ ] You learn well from corrections

**Add Automation if:**
- [ ] You're on a team (need consistency)
- [ ] Violation rate is stable near 0%
- [ ] You want zero-maintenance enforcement
- [ ] You're ready for full CI/CD integration

**Learn Absorb when:**
- [ ] You're comfortable with basic jj workflow
- [ ] You're tired of creating intermediate commits
- [ ] You want cleaner revision history
- [ ] You're in month 2+ of TDD discipline

## Recommendation

**Start with the custom agent for 1 month, then transition to instructions only.**

This gives you:
1. Strong initial training
2. Clear violation feedback
3. Gradual autonomy
4. Long-term sustainable workflow

The instructions file is sufficient for phase 2+. The agent adds value for phase 1 if you want stricter enforcement. Absorb should be learned after you're comfortable with the basic workflow (typically month 2+).

## Next Steps

1. **Weeks 1-2**: Use instructions file + manual vigilance
2. **If >2 violations**: Create custom tdd-red agent
3. **Weeks 3-4**: Track violation rate, learn jj basics
4. **Month 2**: Start using absorb for clean revisions
5. **Month 3+**: Consider automation if working with a team
