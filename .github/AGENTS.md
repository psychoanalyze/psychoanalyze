# PsychoAnalyze Custom Agents

This file documents custom agents available in this workspace. Agents provide specialized workflows with constrained tooling and focused expertise.

## TDD Workflow Agents

### tdd-red

**File:** `.github/agents/tdd-red.agent.md`

**Purpose:** Enforces strict one-test-per-cycle TDD discipline during red phases. Prevents writing multiple tests, validates test atomicity, and guides revision splitting when violations occur.

**When to use:**
- Writing failing tests (red phase)
- Splitting oversized revisions
- Validating TDD atomicity
- Updating d2 diagrams after splits

**Example invocation:**
```
Use the tdd-red agent to write a test for hit rate calculation
```

**Constraints:**
- Writes exactly ONE test per invocation
- Blocks notebook edits
- Enforces atomic behavior testing
- Auto-detects and splits violations

### d2-tdd

**File:** *To be created*

**Purpose:** TDD translator - converts verbose natural language requests into atomic TDD cycles.

**Status:** Stub (listed in global agents but not yet implemented)

## Version Control Agents

### jj-helper

**File:** Global agent (not workspace-specific)

**Purpose:** Jujutsu (jj) version control expert for advanced revision operations.

**When to use:**
- Rebasing revisions
- Resolving conflicts
- Analyzing revision evolution (`jj evolog`)
- Complex revision surgery

**Example invocation:**
```
Use the jj-helper agent to rebase these 3 revisions onto main
```

## Marimo Workflow Agents

### marimo-helper

**File:** Global agent (not workspace-specific)

**Purpose:** Marimo notebook translation and management.

**When to use:**
- Converting Jupyter to Marimo
- Managing Marimo dashboard
- Troubleshooting reactive execution

## Development Workflow Agents

### SE: Architect

**File:** Global agent

**Purpose:** System architecture review specialist with Well-Architected frameworks, design validation, and scalability analysis.

**When to use:**
- Reviewing system design
- Validating architectural decisions
- Scalability analysis

### SE: Tech Writer

**File:** Global agent

**Purpose:** Technical writing specialist for documentation, blogs, tutorials, and educational content.

**When to use:**
- Writing API documentation
- Creating tutorials
- Documenting architecture decisions

### SE: DevOps/CI

**File:** Global agent

**Purpose:** DevOps specialist for CI/CD pipelines, deployment debugging, and GitOps workflows.

**When to use:**
- Setting up GitHub Actions
- Debugging CI/CD pipelines
- Deployment automation

## Agent Development

### Creating New Agents

1. **Create agent file:** `.github/agents/<name>.agent.md`
2. **Define YAML frontmatter:**
   ```yaml
   ---
   name: agent-name
   description: Brief description of purpose
   toolRestrictions:
     - name: tool_name
       restriction: allowed|blocked
   ---
   ```
3. **Document in this file** under appropriate section
4. **Test invocation:** `Use the <name> agent to...`

### Agent Design Principles

- **Single Responsibility:** Each agent has ONE clear purpose
- **Tool Constraints:** Restrict tools to prevent scope creep
- **Clear Invocation:** Description makes it obvious when to use
- **Integration:** Agents should hand off to each other when appropriate

### Tool Restrictions

Common patterns:

```yaml
# Read-only agent (research, analysis)
toolRestrictions:
  - name: replace_string_in_file
    restriction: blocked
  - name: create_file
    restriction: blocked

# Workflow enforcer (strict rules)
toolRestrictions:
  - name: edit_notebook_file
    restriction: blocked
  - name: run_in_terminal
    restriction: allowed

# Full-spectrum (general purpose)
toolRestrictions: []
```

## Usage Guidelines

### When to Use an Agent

Use agents when:
- You need **strict enforcement** of a workflow rule
- You want **constrained tooling** for safety
- You need **specialized expertise** in one domain
- You want **consistent behavior** across sessions

### When NOT to Use an Agent

Don't use agents when:
- General Copilot is sufficient
- You need flexibility across domains
- Constraint overhead > benefit
- Agent isn't well-suited to task

### Agent Chaining

Agents can hand off to each other:

```
[tdd-red] → Write failing test
[default]  → Implement code to pass test
[tdd-red] → Write next failing test
[jj-helper] → Rebase revisions
```

## Metrics & Improvement

Track agent effectiveness:

```nushell
# How often do you invoke agents?
def agent-usage [] {
    git log --since="1 month ago" --grep="agent" --oneline | lines | length
}

# Which agents are most used?
def agent-frequency [] {
    git log --since="1 month ago" --grep="agent" --oneline
    | parse "{commit} {rest}"
    | get rest
    | str downcase
    | where ($it | str contains "agent")
    | parse --regex '(?P<agent>\w+-\w+) agent'
    | get agent
    | uniq -c
}

# What's the violation rate with tdd-red?
def tdd-violations [] {
    jj log --limit 100
    | grep "red phase"
    | each {|line|
        let tests = (jj diff -r ... | grep "^+def test_" | lines | length)
        if $tests > 1 { 1 } else { 0 }
    }
    | math sum
}
```

Review metrics monthly and refine agents based on actual usage patterns.

## References

- **Agent Customization Skill:** `copilot-skill:/agent-customization/SKILL.md`
- **JJ TDD Revisions Skill:** `.github/skills/jj-tdd-revisions/SKILL.md`
- **TDD Enforcement Strategy:** `.github/docs/tdd-enforcement-strategy.md`
- **Revision Splitting Instructions:** `.github/instructions/jj-revision-splitting.instructions.md`
