# Quiz W5 cheat sheet: git concepts + DDD

**The model**

| | |
|---|---|
| **Content-addressed store** | every object is named by the **hash of its content**; same content = same hash |
| **Blob / tree / commit** | file content / directory listing (names → hashes) / root tree + parent(s) + author + message |
| **DAG** | commits point to parents; objects are **immutable** ("editing" history = new commits) |
| **Ref / branch / tag** | mutable pointer to a commit / a ref that moves when you commit / a ref that doesn't move |
| **HEAD / detached** | where you are (a branch) / pointing at a commit directly; new commits there are on no branch |
| **Three trees** | **HEAD** (last commit) · **index** (next commit) · **working dir** (files on disk) |
| **Remote** | another repository; `origin/main` = your copy of its branch |
| **`.git/`** | objects, refs, HEAD, index, config, logs (reflog), hooks |

**Derived concepts (= operations on objects and refs)**

| | |
|---|---|
| `stash` | uncommitted changes saved as commits under `refs/stash`, then reset to HEAD |
| `reset` | moves the branch ref: `--soft` ref · `--mixed` + index · `--hard` + working dir |
| `cherry-pick` | re-applies one commit's change as a **new** commit |
| `rebase` | cherry-picks your commits onto a new base, moves the branch (never on shared commits) |
| `merge` | a commit with 2 parents, or a **fast-forward** (just move the ref) |
| `revert` | a new commit undoing an old one: **safe after a push** |
| `reflog` | local log of where HEAD/branches pointed: recovers "lost" commits |

**Commands (classic form)**

| | |
|---|---|
| `init` / `clone <url>` | new empty repo (creates `.git/`) / copy an existing one |
| `add` → `commit -m` | working dir → index → new commit (branch moves) |
| `fetch` / `pull` / `push` | get objects / fetch + merge / send commits |
| `checkout <b>` / `-b <new>` | switch branch / **create + switch** |
| `checkout <commit>` / `-- <file>` | detached HEAD / discard a file's changes |
| `stash` / `-u` / `list` | shelve / incl. untracked / show the stack |
| `stash pop` / `apply` / `drop` | re-apply + remove / re-apply + keep / delete |
| `reset HEAD <f>` | unstage a file |
| `commit --amend` | redo the last commit (don't if pushed) |

**Production bug mid-feature:** `stash` → `checkout main` → `pull` → `checkout -b hotfix/x` → fix +
commit → push + PR → merge, deploy, tag → `checkout feature` → `stash pop` → `merge main`.
Branch from **main** = what's in production.

**Recovery:** detached-HEAD commits / `reset --hard` / bad rebase / deleted branch → `git reflog` →
find the hash → `checkout -b rescue <hash>` or `reset --hard <hash>`. Uncommitted discarded work
is **not** recoverable (never an object). **Conflict:** fix markers → `add` → `commit`
(`merge --abort`).

**Lab plumbing:** `hash-object` (SHA-1 of `blob <size>\0content`, `-w` stores) · `cat-file -t/-p`
(read by hash) · `write-tree` (index → tree) · `commit-tree` (tree + parent + msg → commit, no ref
moved). `commit` = write-tree + commit-tree + move the branch.

**Ubiquitous-language counterexample:** `checkout` overloaded, `reset` 3 modes, index = staging =
cache, `pull` = fetch + merge.

**DDD**

| | |
|---|---|
| **Domain model** | shared concepts, rules, vocabulary = the team's theory (Naur); the lasting asset when code is cheap |
| **Ubiquitous language** | one name per concept everywhere; names measurably change agent output (severity ≠ priority) |
| **Bounded context** | one model's terms consistent inside; information hiding → small agent context |
| **Anti-corruption layer** | translation layer; vs agents: blocks training-data conventions (LLM output → strict TriageRecord) |
| **Entity / value object** | persisting identity (an issue) / defined by values (a severity, a git blob) |
| **Aggregate / invariant** | changed together via one root / a rule that always holds |
