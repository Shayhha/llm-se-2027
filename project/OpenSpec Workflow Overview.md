## OpenSpec Workflow Overview

OpenSpec is an add-on to coding agents. It is available from https://github.com/Fission-AI/OpenSpec, and the current documentation is at https://openspec.dev/docs (the `docs/` folder in the repo is legacy). It supports "spec-driven" development in a structured manner with LLM support.

This page describes **OpenSpec 2.0** (November 2026). In 2.0 the agent workflow is delivered as **skills** (`/openspec-propose`, ...). The older `/opsx:*` slash commands (1.x) and `/openspec:*` commands (0.x) have been removed.

OpenSpec is a **spec-driven development workflow** that uses structured proposals before implementation. You agree with the agent on *what* to build (a change proposal with spec deltas) before any code is written.

### **Setup**

```bash
npm install -g @fission-ai/openspec@latest   # requires Node.js >= 22.12
# or: brew install openspec
# or: curl -fsSL https://openspec.dev/cli/install.sh | sh

cd your-project
openspec init --tools claude                 # or codex, cursor, github-copilot, all, none
```

`init` creates:

```
openspec/
├── config.yaml     # project context and per-artifact rules for the agent
├── specs/          # current truth: what IS built, one folder per capability
└── changes/        # proposals: what SHOULD change
    └── archive/    # completed changes
```

It also installs the skills in `.agents/skills/openspec-*/` (linked into `.claude/skills/` for Claude Code).

Upgrading an existing project: install the new CLI, then run `openspec update` in the project. It removes legacy files (`openspec/AGENTS.md`, old command files, OpenSpec blocks in `CLAUDE.md`). If you have an old `openspec/project.md`, `init`/`update` prints a prompt for migrating it into `config.yaml`. Delete `project.md` once that is done.

### **The Workflow**

The loop is: **explore (optional) → propose → review → apply → archive**. Skills run in the agent chat. `openspec ...` commands run in the terminal.

0. **Explore (optional): `/openspec-explore`**
    
    - Think through an idea with the agent before committing to a proposal. It writes no code.
      
1. **Propose: `/openspec-propose <change-name or description>`**
    
    - The agent creates `openspec/changes/<change-id>/` with the artifacts, in dependency order:
        - `proposal.md`: Why, What Changes, Capabilities (new / modified), Impact
        - `specs/<capability>/spec.md`: delta specs, the requirement changes per affected capability
        - `design.md` (only when needed): context, goals / non-goals, decisions, risks
        - `tasks.md`: numbered implementation checklist (`- [ ] 1.1 ...`)
    - Validate with `openspec validate <change-id> --strict`
    - **Approval gate**: review the proposal and spec deltas before any code is written. Use `/openspec-update-change` to revise the artifacts. With no instruction it runs a coherence review.
      
2. **Apply: `/openspec-apply-change`**
    
    - The agent implements the tasks in order and checks them off (`- [ ]` → `- [x]`)
    - All work traces back to the approved proposal and spec deltas
      
3. **Archive: `/openspec-archive-change`** (or `openspec archive <change-id> --yes`)
    
    - Merges the change's spec deltas into `openspec/specs/` (the main specs now describe the new behavior)
    - Moves `changes/<id>/` → `changes/archive/YYYY-MM-DD-<id>/`, which keeps an audit trail
    - Validates first, and refuses to archive an invalid change
    - `/openspec-sync-specs` merges the deltas into the main specs without archiving

The default (**core**) profile installs the six skills above: explore, propose, apply, update, sync, archive. Optional skills are enabled with `openspec config profile` followed by `openspec update`:

| Skill | Purpose |
|---|---|
| `/openspec-new-change` | Empty change scaffold, no artifacts yet |
| `/openspec-continue-change` | Write the next ready artifact, one at a time |
| `/openspec-ff-change` | Fast-forward: write all artifacts in one pass |
| `/openspec-verify-change` | Report on completeness / correctness / coherence before archiving |
| `/openspec-bulk-archive-change` | Archive several changes at once |
| `/openspec-onboard` | Guided walkthrough on a real change (~15–20 min) |

(In Codex, skills are invoked with `$` instead of `/`, e.g. `$openspec-propose`.)

### **Delta Spec Format**

A delta spec only describes what changes in a capability:

```markdown
## ADDED Requirements

### Requirement: Escalate low-confidence triage
The system SHALL route an issue to the human queue when extraction confidence is below 0.7.

#### Scenario: Low confidence
- **WHEN** the extractor returns confidence 0.55
- **THEN** the issue is assigned to the `needs-human` queue
```

- Sections: `## ADDED Requirements`, `## MODIFIED Requirements` (repeat the **full** updated requirement, with a matching header), `## REMOVED Requirements` (give a **Reason** and a **Migration**), `## RENAMED Requirements` (FROM:/TO:)
- Each requirement uses SHALL/MUST and has at least one `#### Scenario:` (exactly 4 `#`) with WHEN/THEN steps
- `--strict` treats warnings (e.g., missing WHEN/THEN, very long requirement text) as failures

### **When to Create a Proposal vs. Direct Work**

**Create a proposal for:**

- New features/capabilities
- Breaking changes (API, schema, architecture)
- Performance optimizations that change behavior
- Security pattern updates

**Skip the proposal for:**

- Bug fixes (restoring intended behavior)
- Typos, formatting, comments
- Non-breaking dependency updates
- Configuration changes

### **Key Commands**

```bash
openspec list                       # See active changes
openspec list --specs               # See existing capabilities
openspec view                       # Dashboard of specs and changes
openspec show [item]                # View details (--json, --deltas-only)
openspec status --change <id>       # Which artifacts are done / ready
openspec validate [id] --strict     # Validate a change or spec (--all, --changes, --specs)
openspec archive <change-id> --yes  # Merge deltas into specs and archive
openspec update                     # Refresh skills after upgrading the CLI or changing the profile
```

### **How to Trigger Proposal Creation**

Call `/openspec-propose` with a name or a description:

- `/openspec-propose add-dark-mode`
- `/openspec-propose Let users export their reports as PDF`

If the idea is still vague, start with `/openspec-explore`. The agent will then:

1. Read `openspec/config.yaml` and the existing specs in `openspec/specs/`
2. Check the active changes in `openspec/changes/` for conflicts
3. Create the change folder with proposal, spec deltas (requirements and scenarios), design if needed, and tasks
4. Stop so you can review before `/openspec-apply-change`

### **Key Files for Context**

- `openspec/config.yaml`: project `context` (stack, conventions, domain) and per-artifact `rules`, injected into the agent's instructions for every artifact. It replaces the old `project.md`.
- `openspec/specs/`: current truth of what IS built
- `openspec/changes/`: proposals for what SHOULD change
- `openspec/changes/archive/`: history of completed changes

Customize the workflow through `config.yaml`, not by editing `.agents/skills/openspec-*`, which `openspec update` overwrites.

This approach keeps your codebase organized and changes well documented, and it prevents scope creep: every change has an approved spec before implementation begins.
