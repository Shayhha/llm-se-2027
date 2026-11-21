# Quiz W5 prep: git concepts + domain-driven design

**Scope (syllabus, W4):** DDD principles and the **git case study**: git's basic concepts, the
commands derived from them, and git as a ubiquitous-language counterexample. Plus **Tuesday's lab**
(a mini git + disaster recovery, see section 8). Commands are given in the classic form
(`checkout`, `reset`), as shown in class.

---

## 1. Git's model: the basic concepts

Git is a **content-addressed object store** plus a few **pointers** into it.

| Concept | Meaning |
|---|---|
| **Content-addressed** | every object is stored under the **hash (SHA-1) of its content**. Same content → same hash; change one byte → a new hash. The hash is both the **name** and an **integrity check** |
| **Blob** | the **content of one file** (no name, no date) |
| **Tree** | a **directory listing**: names → blob hashes (files) and tree hashes (sub-folders) |
| **Commit** | points to **one root tree** (the full snapshot) + **parent commit(s)** + author, date, message |
| **DAG of commits** | commits point back to their parents, forming a **directed acyclic graph**. Objects are **immutable**: "changing" history creates new commits |
| **Ref** | a **mutable pointer** (a name → a commit hash, a small file in `.git/refs/`) into the immutable DAG. A **branch** is a ref that **moves forward** when you commit (so creating one is instant); a **tag** never moves (`v1.2.0`) |
| **HEAD** | **where you are**: usually points to a branch (`ref: refs/heads/main`) |
| **Detached HEAD** | HEAD points **directly at a commit**, not a branch; new commits there are reachable from no branch |
| **Remote** | **another repository** (e.g. `origin` on GitHub). `origin/main` = your last-known copy of its branch; `fetch` / `push` copy objects and update refs |

**The three trees:** **HEAD** (the last commit) · the **index** / staging area (the next commit) · the **working directory** (files on disk). `add` = working dir → index; `commit` = index → new commit + branch moves; `checkout` = commit → index + working dir.

**The `.git` folder** is the repository: `objects/` (blobs, trees, commits), `refs/` (branches,
tags, remote branches), `HEAD`, `index`, `config`, `logs/` (the reflog), `hooks/`. Delete it and
the history is gone; the files on disk stay.

**Consequences:** commits are **snapshots, not diffs** (unchanged files reuse blobs); history **can't change silently** (a hash covers tree + parents); objects are only **added**, so a "lost" commit survives until garbage collection and the **reflog** finds it.

## 2. Derived concepts: everything else is built from the model

The syllabus point: stash, rebase, reset, cherry-pick and the reflog are **not new concepts**,
just operations on objects and refs.

| Command | In terms of the model |
|---|---|
| **`git stash`** | saves your uncommitted changes **as commits** (pointed to by the ref `refs/stash`), then resets the working dir and index to HEAD |
| **`git reset <commit>`** | **moves the current branch ref** to `<commit>`. `--soft`: only the ref; `--mixed` (default): ref + index; `--hard`: ref + index + working dir |
| **`git cherry-pick <c>`** | takes the **change** `<c>` introduced (its diff against its parent) and makes a **new commit** with it on the current branch (new hash) |
| **`git rebase <base>`** | cherry-picks your commits one by one onto `<base>`, then **moves your branch ref** to the last new commit. The old commits still exist, unreferenced |
| **`git merge <b>`** | creates a commit with **two parents** (or, if your branch is behind, just **moves the ref**: a fast-forward) |
| **`git reflog`** | a **log of every value HEAD (and each branch) has pointed to**, local only. Since commits aren't deleted, it recovers anything a reset or rebase "lost" |
| **`git revert <c>`** | a **new commit** with the inverse change; nothing is rewritten |

## 3. Basic commands

```bash
git init               # new empty repo here (creates .git/)
git clone <url>        # copy an existing repo with all history
git status             # what changed / what is staged
git add <file>         # stage (git add . = everything)
git commit -m "msg"    # save a snapshot, branch moves
git log --oneline      # history (--graph --all: the DAG)
git diff [--staged]    # unstaged [staged] changes
git fetch / pull       # get objects (pull = fetch + merge)
git push               # send commits, update remote ref
git remote add origin <url>   # connect to another repo
```

**`.gitignore`** lists what git must not track: build output, `.venv`, **`.env` with secrets**.

**`git checkout`** (the overloaded command):

| Form | Does |
|---|---|
| `git checkout <branch>` | **switch** to a branch (HEAD → that branch; files updated) |
| `git checkout -b <new>` | **create a branch and switch to it** |
| `git checkout <commit>` | go to an old commit → **detached HEAD** |
| `git checkout -- <file>` | **discard** a file's uncommitted changes (copy it from the index) |
| `git checkout <branch> -- <file>` | take a file's version from another branch |

Git **refuses to switch** if uncommitted changes would be overwritten: commit or stash first.

**`git stash`:** shelve uncommitted changes (`-u`: include untracked files) · `stash list` (stack `stash@{0}`, `{1}`…) · **`pop`** = re-apply **and remove** · **`apply`** = re-apply **and keep** · `drop` / `clear`. Local only; `pop` can conflict.

**Undo:** unstage `git reset HEAD <file>` · redo the last commit `git commit --amend` (not if pushed) · undo last commit `git reset --soft HEAD~1` · undo a **pushed** commit `git revert <hash>`.

## 4. Branches, merging, conflicts

**Create a branch and move into it: `git checkout -b feature/login`** · create only `git branch x` · move `git checkout main` · list `git branch -a` · delete `git branch -d x` · publish `git push -u origin x` · merge into current `git checkout main` → `git merge x`.

**Merge vs rebase:** true history (2-parent commit) vs linear history (rewritten commits); **never rebase commits others have**.

**Conflict:** both sides changed the same lines; git marks them
(`<<<<<<< HEAD` yours `=======` theirs `>>>>>>> feature`). Edit → `git add` → `git commit`
(or `git rebase --continue`). Cancel with `git merge --abort` / `git rebase --abort`.

**Strategies:** feature branch + **PR** · **Git Flow** (`main`, `develop`, `feature/*`, `release/*`, **`hotfix/*` from `main`**) · **trunk-based** (short branches, CI).

## 5. Scenario: a production bug while you're on your own branch

You're on `feature/search` with **unfinished changes**; `main` (production) has an urgent bug.

1. **Save your work:** `git stash` (or `git commit -m "WIP"`).
2. **Go to production and update:** `git checkout main` → `git pull`
3. **Branch off it:** `git checkout -b hotfix/login-crash`
4. **Fix, test, commit:** `git add …` → `git commit -m "Fix login crash"`
5. **Push + PR into main:** `git push -u origin hotfix/login-crash` → review → merge → deploy,
   tag `v1.2.1`.
6. **Back to your work:** `git checkout feature/search` → `git stash pop`
7. **Get the fix too:** `git merge main` (or `git cherry-pick <fix-hash>`).

**Why:** the fix starts from **what is in production**, not your half-done feature; your work isn't
mixed in; the fix is reviewed; your branch gets the fix so it doesn't come back.

## 6. Disaster recovery (the lab's second part)

| Disaster | What happened (model) | Recovery |
|---|---|---|
| **Commits made in detached HEAD**, then checked out a branch | the commits exist, but **no ref** points to them | `git reflog` → find the hash → `git checkout -b rescue <hash>` (or `git branch rescue <hash>`) |
| **Lost commits** after `git reset --hard` | the branch ref moved back; the commits are unreferenced | `git reflog` → `git reset --hard <hash>` |
| **Botched rebase** | the branch now points to new, wrong commits; the old ones still exist | `git rebase --abort` while it runs; afterwards `git reflog` → `git reset --hard <branch>@{n}` (the pre-rebase position; also `ORIG_HEAD`) |
| **Deleted a branch** | only the ref is gone | `git reflog` → `git branch <name> <hash>` |

**Lesson:** objects are immutable and only refs move, so recovery = find the old hash (reflog) and point a ref at it. **Uncommitted** discarded work can't be recovered (never an object); the reflog is local and expires.

## 7. Git as a ubiquitous-language counterexample

A **clean model** (objects, refs, HEAD, three trees) with an **inconsistent language**: `checkout` does unrelated things (hence `switch`/`restore` in Git 2.23), `reset` has 3 meanings and also unstages, **index = staging area = cache**, `pull` hides fetch + merge. Bad names → people **and agents** misuse the tool.

---

## 8. Tuesday's lab (from the syllabus)

**Part 1: a mini git in ~100 lines**, implementing git's low-level ("**plumbing**") commands:

| Command | What it does |
|---|---|
| **`hash-object`** | computes a file's hash: SHA-1 of `"blob <size>\0" + content`, and (with `-w`) stores it zlib-compressed in `.git/objects/ab/cdef…` (first 2 hex chars = folder) |
| **`cat-file`** | reads an object back by hash: its type (`-t`), size (`-s`) or content (`-p`) |
| **`write-tree`** | turns the **index** into a tree object (and sub-trees) and prints its hash |
| **`commit-tree`** | creates a commit from a tree hash + optional parent (`-p`) + message, prints its hash. It does **not** move any branch (`git update-ref` / `git commit` does that) |

`git commit` = `write-tree` + `commit-tree` + moving the branch ref. "Porcelain" commands
(add, commit, checkout) are built on these.

**Part 2: deliberate disaster recovery:** detached HEAD, lost commits, botched rebase, recovery
via the reflog (section 6).

---

## 9. Domain-Driven Design (DDD)

**Domain model:** a shared model of the problem's concepts, rules and vocabulary. It is the
team's **theory of the program** (Naur, W1). **When code is cheap** (agents write it), this model
is the lasting asset, and it must be **written down** (glossary, invariants, specs).

| Concept | Meaning | Example (our triage system) |
|---|---|---|
| **Ubiquitous language** | **one agreed name per concept**, everywhere: talk, specs, code. A **machine-readable interface**: **names measurably change what agents generate** | "severity" = how bad a bug is, never "priority" (W1's `ticket_priority` broke this) |
| **Bounded context** | a boundary inside which one model's terms are consistent; the same word may mean something else elsewhere. Gives **information hiding** and a **small, focused agent context** | "component" = a code folder in *routing*, free text in *enrichment* |
| **Anti-corruption layer (ACL)** | a **translation layer** that keeps an outside model from leaking into yours. Reinterpreted: insulation against **conventions the agent imports from its training data** | validating LLM output into our `TriageRecord` (rejecting "High", `feature-request`) |
| **Entity** | has an **identity** that persists while its data changes | an issue (repo + number) |
| **Value object** | defined only by its **values**, immutable | a severity level |
| **Aggregate / invariant** | objects changed together through one root / a rule that always holds | "every security issue goes to the security queue" (W2) |

**With agents:** they guess what the model leaves unstated; a written glossary + boundaries give them the right context. Git's objects are a good domain model (a blob is a **value object**: identity = content); its command names break the ubiquitous language.

---

## Practice Q&A

1. What does "content-addressed" mean in git?<details><summary>Answer</summary>Each object is stored and named by the hash of its content, so identical content gets the same hash and any change gives a new one. The hash is also an integrity check.</details>
2. What are blobs, trees and commits?<details><summary>Answer</summary>Blob = a file's content; tree = a directory listing (names → blob/tree hashes); commit = a root tree + parent(s) + author, date and message.</details>
3. What is a branch, in terms of the model? Why is creating one cheap?<details><summary>Answer</summary>A ref: a mutable pointer (a small file) holding a commit hash, which moves forward when you commit. Creating one only writes that file; nothing is copied.</details>
4. What does "refs are mutable pointers into an immutable DAG" mean?<details><summary>Answer</summary>Commits (and all objects) never change and point to their parents, forming a DAG; only refs (branches, HEAD) change, by pointing to different commits.</details>
5. What is HEAD? What is a detached HEAD, and what's the risk?<details><summary>Answer</summary>HEAD is where you are, normally a branch. Detached = pointing at a commit directly; new commits there are reachable from no branch and can be "lost" once you leave.</details>
6. What are git's three trees, and what do `add` and `commit` do to them?<details><summary>Answer</summary>HEAD (last commit), the index (next commit), the working directory (files on disk). add copies working dir → index; commit makes the index a new commit and moves the branch.</details>
7. What is a remote?<details><summary>Answer</summary>Another repository (e.g. origin on GitHub). Fetch/push copy objects between repositories and update refs; origin/main is your local copy of its branch.</details>
8. Does git store diffs or snapshots? Why can't history be changed silently?<details><summary>Answer</summary>Snapshots (each commit has a full root tree; unchanged files reuse blobs). A commit's hash covers its tree and parents, so changing an old commit changes all later hashes.</details>
9. Explain `git stash` in terms of the model. `pop` vs `apply`?<details><summary>Answer</summary>It saves uncommitted changes as commits under refs/stash and resets to HEAD. pop re-applies and removes the stash; apply re-applies and keeps it.</details>
10. What does `git reset` really do? soft vs mixed vs hard?<details><summary>Answer</summary>Moves the current branch ref to another commit. soft: only the ref; mixed (default): ref + index; hard: ref + index + working directory.</details>
11. What do cherry-pick and rebase do, and why do rebased commits get new hashes?<details><summary>Answer</summary>Cherry-pick re-applies one commit's change as a new commit; rebase cherry-picks a series onto a new base and moves the branch. New parents → new commit hashes, so never rebase commits others already have.</details>
12. Reset vs revert?<details><summary>Answer</summary>Reset moves the branch back, rewriting history (local only). Revert adds a new commit undoing a change, so it's safe after pushing.</details>
13. What is the reflog, and why can it recover "lost" commits?<details><summary>Answer</summary>A local log of every commit HEAD and each branch pointed to. Objects are never deleted right away, so you find the old hash and point a ref at it again.</details>
14. You made commits in detached HEAD and then checked out main. Recover them.<details><summary>Answer</summary>`git reflog` → find the last commit's hash → `git checkout -b rescue <hash>` (or `git branch rescue <hash>`).</details>
15. A rebase went wrong and finished. How do you undo it?<details><summary>Answer</summary>`git reflog` → find the branch's pre-rebase position → `git reset --hard <hash>` (or ORIG_HEAD). During the rebase: `git rebase --abort`.</details>
16. Production has a bug while you're mid-feature. What do you do?<details><summary>Answer</summary>`git stash` → `git checkout main` → `git pull` → `git checkout -b hotfix/x` → fix and commit → push + PR into main → merge, deploy, tag → `git checkout feature` → `git stash pop` → `git merge main`. Branch from main: it's what's in production, not your unfinished work.</details>
17. What do `hash-object`, `cat-file`, `write-tree` and `commit-tree` do?<details><summary>Answer</summary>Hash (and store) a file as a blob; read an object by hash; turn the index into a tree; create a commit from a tree + parent + message (without moving a branch).</details>
18. Why is git a ubiquitous-language counterexample?<details><summary>Answer</summary>A clean model but inconsistent names: checkout does unrelated things, reset has three meanings, and index = staging area = cache.</details>
19. What is a domain model, and why does it matter more when agents write code?<details><summary>Answer</summary>The shared concepts, rules and vocabulary: the team's theory of the program. Code is cheap, so the model is the lasting asset, and agents guess anything it leaves out.</details>
20. What is ubiquitous language? Example?<details><summary>Answer</summary>One agreed name per concept, used everywhere including code; names measurably change agent output. E.g. "severity" never called "priority".</details>
21. What is a bounded context, and how does it help AI context management?<details><summary>Answer</summary>A boundary inside which one model's terms are consistent. Like information hiding, it lets an agent work with only that context's model, keeping its context small.</details>
22. What is an anti-corruption layer, reinterpreted for agents?<details><summary>Answer</summary>A translation layer keeping an outside model out of yours; for agents, insulation against conventions imported from training data (e.g. validating LLM output into a strict TriageRecord).</details>
23. Entity vs value object? Which is a git blob?<details><summary>Answer</summary>An entity has a persisting identity (an issue); a value object is defined by its values (a severity). A blob is a value object: its identity is its content hash.</details>
