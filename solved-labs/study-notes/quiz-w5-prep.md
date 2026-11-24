# Quiz W5 prep: git concepts + domain-driven design

**Sources:** the lecturer's `mental_model/Git Mental Model.md` and `Mental Models of Software Projects.md` + the syllabus.

**Scope (syllabus, W4):** DDD principles and the **git case study**: git's basic concepts, the
commands derived from them, and git as a ubiquitous-language counterexample. Plus **Tuesday's lab**
(a mini git + disaster recovery, see section 8). Commands are given in the classic form
(`checkout`, `reset`), as shown in class.

---

## 1. Git's model: the basic concepts

Git is a **content-addressed object store** plus a few **pointers** into it.

**The lecturer's mental model of git (5 ideas):**
1. **Stream of snapshots:** each commit is a picture of all files; unchanged files are just a link to the already-stored copy.
2. **Local operations:** the full history is in the local database (`.git`), so most commands need no network. A remote (GitHub) is the same kind of database, shared by the team.
3. **Integrity by design:** everything is **checksummed (SHA-1, 40 hex chars)** before it is stored and referred to by that checksum; content is stored by hash, **not by file name**. Nothing changes without git knowing.
4. **Git only adds data:** almost every action adds to the database, so almost everything can be undone.
5. **Three states:** files are **modified**, **staged** or **committed**.

| Concept | Meaning |
|---|---|
| **Content-addressed** | every object is stored under the **hash (SHA-1) of its content**. Same content → same hash; change one byte → a new hash. The hash is both the **name** and an **integrity check** |
| **Blob** | the **content of one file** (no name, no date) |
| **Tree** | a **directory listing**: names → blob hashes (files) and tree hashes (sub-folders) |
| **Commit** | points to **one root tree** (the full snapshot) + **parent commit(s)** (0 for the first commit, 1 normally, 2+ for a merge) + author, committer, date, message |
| **DAG of commits** | commits point back to their parents, forming a **directed acyclic graph**. Objects are **immutable**: "changing" history creates new commits |
| **Ref** | a **mutable pointer** (a name → a commit hash, a small file in `.git/refs/`) into the immutable DAG. A **branch** is a ref that **moves forward** when you commit (so creating one is instant); a **tag** never moves (`v1.2.0`) |
| **HEAD** | **where you are**: usually points to a branch (`ref: refs/heads/main`) |
| **Detached HEAD** | HEAD points **directly at a commit**, not a branch; new commits there are reachable from no branch |
| **Remote** | **another repository** (e.g. `origin` on GitHub). `origin/main` = your last-known copy of its branch; `fetch` / `push` copy objects and update refs |

**The three trees / sections:** **HEAD** (the last commit) · the **index** / staging area (the next commit) · the **working directory** (files on disk). `add` = working dir → index; `commit` = index → new commit + branch moves; `checkout` = commit → index + working dir.
- **Working tree:** one checkout of one version, unpacked from the database. **Staging area:** a file in `.git` (technical name: the **index**). **Git directory:** the metadata + object database, the most important part, and **what is copied when you clone**.
- **File lifecycle:** **untracked** →(add)→ **staged**; **unmodified** →(edit)→ **modified** →(add)→ **staged** →(commit)→ **unmodified**; remove → untracked.
- Modify a file, `add` it, then modify it again: the **second change is not staged**; the file shows as both staged and modified.

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
| **`git merge <b>`** | **fast-forward:** if the target commit is a **descendant** of yours (no divergent work), git just **moves the pointer**. **Three-way merge:** if histories diverged, git combines the two tips and their **common ancestor** into a new snapshot and a **merge commit** (2 parents) |
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

**Conflict:** both branches changed the **same part of the same file** relative to the common ancestor. Git **pauses** the merge (no merge commit); `git status` lists **unmerged paths** ("both modified"); git marks them
(`<<<<<<< HEAD` yours `=======` theirs `>>>>>>> feature`). Edit → `git add` (**marks it resolved**) → `git commit` (finishes the merge)
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

**Porcelain vs plumbing:** porcelain = user-level commands (branches, commits, tags, staging, remotes); plumbing = low-level commands on the primitive objects and the three sections.

**Part 1: a mini git in ~100 lines**, implementing git's low-level ("**plumbing**") commands:

| Command | What it does |
|---|---|
| **`hash-object`** | computes a file's hash: SHA-1 of `"blob <size>\0" + content`, and (with `-w`) stores it zlib-compressed in `.git/objects/ab/cdef…` (first 2 hex chars = folder) |
| **`cat-file`** | reads an object back by hash: its type (`-t`), size (`-s`) or content (`-p`) |
| **`write-tree`** | turns the **index** into a tree object (and sub-trees) and prints its hash |
| **`commit-tree`** | creates a commit from a tree hash + optional parent (`-p`) + message, prints its hash. It does **not** move any branch (`git update-ref` / `git commit` does that) |

More plumbing from the lecturer's notes:
- **`update-index --add --cacheinfo <mode> <hash> <name>`**: put an entry in the index (staging) by hand. Modes: `100644` normal file, `100755` executable, `120000` symlink (`040000` = a tree in a listing).
- **`update-ref refs/heads/main <hash>`**: set a ref safely (a branch is just a file holding a hash, e.g. `echo <hash> > .git/refs/heads/main`).
- **`symbolic-ref HEAD [refs/heads/test]`**: read or set HEAD. HEAD is a **symbolic reference**: it points to **another ref**, not a hash (`ref: refs/heads/main`); `git commit` uses the commit it resolves to as the parent.
- An object is stored at `.git/objects/` + **first 2 hash chars (folder) + the other 38 (file name)**; the hash covers a **header + the content**. `main^{tree}` = the tree of main's last commit.
- **Tag object** (a 4th object type, made by `git tag -a`): tagger, date, message and a pointer to a commit; like a branch that **never moves**.

`git commit` = `write-tree` + `commit-tree` + moving the branch ref. "Porcelain" commands
(add, commit, checkout) are built on these.

**Part 2: deliberate disaster recovery:** detached HEAD, lost commits, botched rebase, recovery
via the reflog (section 6).

---

## 9. Mental models: Naur's theory and DDD

**Naur, *Programming as Theory Building* (1985):** programming mainly produces a **theory** held by the team: knowledge of how part of the world is handled by the program, which lets you **do it, explain it, justify it and answer questions about it** (Ryle's notion of theory).
- **Evidence:** (1) group B extended group A's compiler with **full source, design documents and access to A**, yet its patches "destroyed the power and simplicity" of the design; A saw this instantly. (2) The authors of a 200,000-line real-time system found faults from their own knowledge + code; other teams with full documentation kept getting stuck.
- **Conclusion:** the theory can't be fully written down; it lives in people. A program is **alive** while a team holding its theory controls it and **dies** when the team dissolves; reviving it from documentation alone is "strictly impossible".
- **Three capabilities the theory gives:** (1) **relate the program to the world** (which code ↔ which part of the world, what is relevant); (2) **justify the design**; (3) **respond to change** by **extending** the design, not patching it. All rely on noticing similarities, which can't be written as rules.
- **Lecturer's note:** "system 1"-like AI makes "can't be expressed" less convincing, but owning a project still means you can explain, justify and adapt it.

**Git example:** user 1 knows the commands (add, commit, checkout -b, merge); user 2 holds the **model** (snapshots, content-hash storage, git only adds data, three states, a branch is a pointer) and can **derive** behavior: branching is cheap (one pointer), fast-forward = the target is a descendant, a "lost" commit is recoverable (nothing erased), a conflict = both branches changed the same region vs a common ancestor. User 1 is like **group B**: full documentation, stuck at the first surprise.

**Theory vs specs:** a spec is a finite set of explicit statements about **what** the system must do: an **output** (snapshot) of the theory. The theory is **why** these requirements and not others, what is central vs incidental, and where the design can stretch. **Two teams with the same spec but different theories will answer the next change request incompatibly.**

**DDD (Evans, 2003)** gives *practices* to build the theory deliberately, share it and keep code aligned:
- **Domain model** = a deliberately selective abstraction of what the team knows; the shared understanding, not a diagram. Built by **knowledge crunching**: developers + domain experts iterate over examples, find gaps, rebuild.
- Naur ↔ DDD: relate to the world ↔ **model-driven design** (code structure mirrors the model); justify ↔ arguing design **in domain terms**; respond to change ↔ **refactoring toward deeper insight** (revise the model, don't bolt on special cases).
- **Ubiquitous language = the shared, visible part of the theory.** A vocabulary isn't a theory, but it does 3 jobs: **transmission** (newcomers learn by being corrected), **detecting drift** (if a change can't be phrased naturally, it would be a patch), **binding code to theory** (code names = domain terms). Git's UL: blob, tree, commit, ref, HEAD, index, working tree.
- **Bounded context = the scope of one team's theory**; a **context map** describes how different teams' theories relate.
- **Naur vs DDD:** Naur says the theory **can't** be expressed and there's no right method; DDD is more optimistic (make most of it explicit) and is patterns, not a procedure.
- **With AI agents:** the UL is the **cheapest part of the theory to give an LLM**: a glossary in the instructions, specs that must use the terms (e.g. OpenSpec capabilities `issue-enrichment`, `issue-routing`), and **rejecting code that brings synonyms or new concepts**. The team stays responsible for relevance, for when the model must change, and for the code's integrity with the theory.

## 10. Domain-Driven Design (DDD) concepts

**When code is cheap** (agents write it), the domain model is the lasting asset, and as much of it as possible must be **written down** (glossary, invariants, specs).

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
24. What are the 5 ideas in the lecturer's git mental model?<details><summary>Answer</summary>Stream of snapshots; local operations (full history in .git); integrity by SHA-1 checksums, content stored by hash; git only adds data; three states (modified, staged, committed).</details>
25. What are the three states of a file, and the three sections of a project?<details><summary>Answer</summary>Modified, staged, committed; the working tree, the staging area (index) and the git directory (what clone copies).</details>
26. You edit a file, `git add` it, and edit it again. What will `git commit` include?<details><summary>Answer</summary>Only the staged (first) version; the second change stays modified and unstaged.</details>
27. When is a merge a fast-forward, and when a three-way merge?<details><summary>Answer</summary>Fast-forward when the target is a descendant of the current commit (no divergent work): the pointer just moves. Otherwise git merges the two tips with their common ancestor into a new merge commit with 2 parents.</details>
28. What is a symbolic reference? Give the example.<details><summary>Answer</summary>A ref that points to another ref, not a hash: HEAD contains `ref: refs/heads/main`. Read/set with `git symbolic-ref`.</details>
29. What is Naur's main claim, and what is his evidence?<details><summary>Answer</summary>Programming builds a theory held by the team, which documentation can't fully capture. Group B, with full source and docs, still broke group A's compiler design; a 200k-line system's own team found faults others couldn't.</details>
30. What three capabilities does holding the theory give?<details><summary>Answer</summary>Relate the program to the world, justify the design, and respond to change by extending rather than patching.</details>
31. Theory vs spec?<details><summary>Answer</summary>A spec is an explicit snapshot of what the system must do; the theory is why, what's central, and where it can stretch. Same spec + different theories → incompatible answers to the next change.</details>
32. What 3 jobs does the ubiquitous language do for the theory?<details><summary>Answer</summary>Transmission (newcomers corrected on terms), detecting drift (awkward phrasing = a patch coming), and binding code to theory (code names = domain terms).</details>
33. How do the two git users illustrate Naur?<details><summary>Answer</summary>One knows commands, one holds the model and can derive behavior (cheap branches, fast-forward, recovery, conflicts). The command-only user is like group B: full docs, stuck at the first surprise.</details>
