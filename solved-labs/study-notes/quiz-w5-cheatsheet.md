# Quiz W5 cheat sheet: git + DDD

**Concepts**

| | |
|---|---|
| **Commit** | a snapshot of the project + message + parent; identified by a hash |
| **Branch** | a movable pointer to a commit; cheap to create |
| **HEAD / detached** | where you are (a branch) / pointing at a commit directly |
| **Staging area (index)** | what goes into the next commit |
| **Remote (`origin`)** | another copy of the repository (GitHub) |
| **`.git/`** | the repository: objects (history), refs, HEAD, index, config, reflog, hooks |

**Commands**

| | |
|---|---|
| `git switch -c <b>` | **create a branch and move into it** (`checkout -b`) |
| `git switch <b>` | move to a branch |
| `git add` → `git commit -m` | stage → save a snapshot |
| `git pull` / `git push` | get others' work (fetch + merge) / send yours |
| `git merge <b>` | join `<b>` into the current branch |
| `git rebase <b>` | replay your commits on top of `<b>` (never on shared commits) |
| `git stash` / `stash pop` | shelve unfinished work / bring it back |
| `git cherry-pick <hash>` | copy one commit onto this branch |
| `git restore <f>` / `--staged` | discard file changes / unstage |
| `git commit --amend` | fix the last commit (before pushing) |
| `git reset --soft/--mixed/--hard` | undo commits: keep staged / keep unstaged / discard |
| `git revert <hash>` | a new commit undoing an old one: **safe after a push** |
| `git reflog` | every place HEAD has been: recover "lost" commits |

**Production bug while on your feature branch**

`stash` (or a WIP commit) → `switch main` → `pull` → `switch -c hotfix/x` → fix + commit →
`push` + PR into main → merge, deploy, tag → `switch` back → `stash pop` → `merge main`.
Start from **main** = what's in production, not your unfinished feature.

**Conflicts:** fix the `<<<<<<< ======= >>>>>>>` markers → `git add` → `git commit`
(`git merge --abort` cancels).

**Strategies:** feature branch + PR · **Git Flow** (main, develop, feature, release, **hotfix
from main**) · trunk-based (short branches, CI).

**DDD**

| | |
|---|---|
| **Domain model** | the shared concepts, rules and vocabulary = the team's theory of the program (Naur); the lasting asset when code is cheap |
| **Ubiquitous language** | one name per concept, everywhere; names change what agents generate (severity ≠ priority) |
| **Bounded context** | a boundary where one model's terms are consistent; keeps an agent's context small |
| **Anti-corruption layer** | translates an outside model (e.g. LLM output → strict TriageRecord) so it can't leak in |
| **Entity / value object** | has a persisting identity (an issue) / defined by its values (a severity) |
| **Aggregate / invariant** | objects changed together through one root / a rule that always holds |
| **Git as the example** | a good model, an inconsistent language: `checkout` overloaded, 3 `reset` modes, index = staging = cache |
