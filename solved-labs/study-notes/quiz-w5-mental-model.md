# Quiz W5: the lecturer's mental model notes

**Based on** `mental_model/Git Mental Model.md` (Part A, the main file) and
`Mental Models of Software Projects.md` (Part B), in the same order.

## Part A: Git Mental Model

### 1. The mental model

| Idea | What it says |
|---|---|
| **Stream of snapshots** | each commit = a **picture of all files**; unchanged files aren't stored again, just **linked** to the stored copy |
| **Local operations** | the **full history is in the local database** (`.git`), so most commands need no network. To share, **push** to a server (GitHub) with **the same functionality** as a local database; pull / clone from it |
| **Data integrity** | everything is **checksummed (SHA-1, 40 hex chars)** before storing and referred to by it; content is stored **by hash, not by file name**, so no change goes unnoticed |
| **Git only adds data** | almost every action **only adds**, so a committed snapshot is hard to lose and you can **almost always undo** |
| **3 states** | **modified** (changed, not committed) · **staged** (marked for the next commit) · **committed** (stored in the database) |

**3 sections:** **working tree** (one checkout of one version, on disk) · **staging area** (a file in `.git`, technical name **index**) · **git directory** (metadata + object database; **what clone copies**).
**Workflow:** checkout → modify → **selectively stage** → commit (stores the staged snapshot permanently).

**Porcelain** = user-level commands (branches, commits, tags, staging, remotes). **Plumbing** = low-level commands on the **primitive objects** and the **3 sections**.

### 2. Porcelain view

- **Create a repo:** `git init` in an existing directory (then `add` + `commit`), or `git clone <url>`.
- **File lifecycle:** untracked →(add)→ staged; unmodified →(edit)→ modified →(stage)→ staged →(commit)→ unmodified; remove → untracked.
- **`git status`:** "working tree clean" / "Untracked files" / "Changes to be committed". **Trap:** stage a file, then edit it again → it shows as **both staged and modified**; only the staged version is committed.
- **`git log`:** commits of the current branch, **newest first**; each has message, author, date, **SHA-1** and its **parent**.
- **Remotes:** one repo can have **several**; **push** sends, **fetch** gets; `git remote -v` lists them.
- **Tags:** mark releases; `git tag -a v1.4 -m "…"` (annotated), `git show v1.4`.

### 3. Branching

**A branch is just a pointer to a commit**, so creating and switching are cheap. A **commit** holds a pointer to its snapshot, author, message and **parents: 0** (first), **1** (normal), **2+** (merge).

**The `iss53` + hotfix scenario:**

| Step | Command | Graph |
|---|---|---|
| Start | | C0←C1←C2; `main`→C2, **HEAD→main** |
| New branch | `git checkout -b iss53` (= `branch` + `checkout`) | only a **new pointer** iss53→C2; HEAD→iss53 |
| Commit | `git commit -a -m …` | C3; **iss53 moves** (HEAD points to it) |
| Urgent bug | `git checkout main` | working dir = **exactly** main's last commit |
| Hotfix | `git checkout -b hotfix`, commit | C4 (parent C2) |
| Deploy | `git checkout main` → `git merge hotfix` | **fast-forward**: main→C4; then `git branch -d hotfix` |
| Back to work | `git checkout iss53`, commit | C5; **the fix isn't in iss53** (use `git merge main` if needed) |
| Finish | `git checkout main` → `git merge iss53` | **three-way merge** → C6, parents C4 + C5 |

- **Switching:** git **refuses** if uncommitted changes conflict with the target branch: commit or **stash** first.
- **Fast-forward:** the merged commit is **directly ahead** (a descendant) → no divergent work → git **just moves the pointer**.
- **Three-way merge:** histories **diverged** → git uses the **2 tips + their common ancestor** (C2) → a new snapshot and a **merge commit with 2+ parents**.
- **Conflict:** the **same part of the same file** changed in both. Git **pauses** (no merge commit), `git status` shows **"Unmerged paths / both modified"**. Markers: `<<<<<<< HEAD` (your branch) `=======` (theirs) `>>>>>>> iss53`. Fix manually → **`git add`** (marks resolved) → **commit** (finishes the merge).
- **Rebase:** replays your commits onto the other branch as **new commits** (linear history). **Don't rebase commits others have**; use a three-way merge.

### 4. Plumbing view

**`.git` key parts:** **objects** (all content) · **refs** (pointers to commits: branches, tags, remotes) · **HEAD** (the checked-out branch) · **index** (staging).

**Objects** are named by a **40-char hash** of their content: **immutable pointers to immutable nodes** in a graph. Types: **blob** (file content), **tree** (folder), **commit** (points to a tree), **tag**.

| Command | What it does |
|---|---|
| `git hash-object [-w] [--stdin]` | hash content (+ header); **`-w` stores** it at `.git/objects/<2 chars>/<38 chars>` |
| `git cat-file -p / -t <hash>` | print an object's content / type |
| `git update-index --add --cacheinfo <mode> <hash> <name>` | put an entry in the **index** by hand |
| `git write-tree` | write the **index** as a **tree** object |
| `git commit-tree <tree> [-p <parent>]` | create a **commit**; message from stdin (`echo msg` piped in); no branch moves |
| `git update-ref refs/heads/<b> <hash>` | create / move a **branch** safely |
| `git symbolic-ref HEAD [refs/heads/<b>]` | read / set **HEAD** |

- **Blob versions:** storing "version 1" then "version 2" gives **2 blobs**; either can be restored with `cat-file -p <hash> > file`. But blobs have **no file name** → trees.
- **Trees** = like a simplified UNIX file system; each entry = **mode, type, hash, name**. `main^{tree}` = main's last commit's tree. Modes: **100644** file, **100755** executable, **120000** symlink (`040000` = sub-tree).
- **Commits** add **who, when, why**: `tree`, `parent`, author/committer (`user.name`, `user.email`, timestamp), message. Chaining `commit-tree -p` builds a real history **without porcelain**.
- **`git add` + `git commit`** = store blobs, update the index, write trees, write a commit pointing to the top tree + the previous commit.
- **Refs:** a file in `.git/refs/heads` holding a hash. **A branch = a pointer to the head of a line of work**.
- **HEAD** is a **symbolic reference**: it points to **another ref**, not a hash (`ref: refs/heads/main`). `git checkout test` changes it to `ref: refs/heads/test`. `git commit` uses **the commit HEAD's branch points to** as the parent.
- **Tag object** (4th type): tagger, date, message, pointer to a **commit**; a name that **never moves**.

## Part B: Mental Models of Software Projects

### 5. Naur: programming as theory building (1985)

- Programming mainly produces a **theory** the team holds about how the program handles part of the world. "Theory" (Ryle) = knowledge to **do** something and **explain, justify and answer questions** about it.
- **Case 1:** group B extended group A's **compiler** with **full source, design docs and access to A**, yet its patches "destroyed the power and simplicity" of the design; A saw it instantly.
- **Case 2:** the team of a **200,000-line real-time system** found faults from **knowledge + code**; other teams with full documentation struggled.
- **Conclusion:** the theory **can't be expressed**; it lives in people. A program is **alive** while a team holding its theory controls it and **dies** when the team dissolves; reviving it from documentation is "strictly impossible".
- **3 capabilities of the theory:** (1) **relate the program to the world** and decide what's relevant; (2) **justify the design**; (3) **respond to change** by **extending, not patching**. All need **noticing similarities**, which can't be written as rules.
- **Lecturer's note:** "system 1"-like AI makes "can't be expressed" **less convincing**, but owning a project still = **explain, justify, adapt**.

### 6. The git example; theory vs specs

- **User 1 knows commands** (add, commit, checkout -b, merge). **User 2 holds the model** (snapshots, content hashes, only adds, 3 states, branch = pointer) and **derives** behavior: cheap branches (one pointer), fast-forward (target is a descendant), recoverable "lost" commits (nothing erased), conflicts (same region vs a common ancestor). **User 1 = group B**: has the docs, stuck at the first surprise.
- Code, specs and design **come out of** the shared understanding; writing them is **how** a team builds the model.
- **Spec** = a finite, explicit list of **what** the system must do: one **output / snapshot** of the theory. **Theory** = **why** these requirements, what's irrelevant, central vs incidental, where the design can stretch. **Same spec + different theories → incompatible answers to the next change.**

### 7. Theory, DDD and ubiquitous language

- **DDD (Evans, 2003)** = practices to build the theory **on purpose**, share it and keep code aligned.
- **Domain model** = a **selective abstraction** of the team's knowledge: the **shared understanding**, not a diagram. Built by **knowledge crunching** (developers + domain experts iterate on examples, find gaps, rebuild).

| Naur's capability | DDD practice |
|---|---|
| relate to the world / relevance | **model-driven design**: code structure mirrors the model |
| justify the design | argue in **domain terms** ("a Leg belongs to an Itinerary because…") |
| respond to change | **refactoring toward deeper insight**: revise the model, no special cases |

- **Ubiquitous language = the shared, visible part of the theory**: one vocabulary in talk, specs, tests and code. Not a theory itself, but it does **3 jobs**: **transmission** (newcomers corrected on terms), **detecting drift** (a change that can't be phrased naturally = a patch coming), **binding code to theory** (identifiers = domain terms). Git's UL: blob, tree, commit, ref, HEAD, index, working tree.
- **Bounded context** = where a model's language holds ("Customer" in billing ≠ shipping), usually one team: **the scope of one team's theory**. A **context map** relates teams' theories.
- **Naur vs DDD:** expressible? Naur **no**, DDD **mostly yes** (the AI note leans to DDD). Method? Naur: **no right method**; DDD: **patterns, not a procedure** (Naur accepts aids).

### 8. With AI agents

The UL is the **cheapest part of the theory to give an LLM**: a **glossary** in its instructions, specs that **use the terms** (OpenSpec `issue-enrichment`, `issue-routing`), and **rejecting code with synonyms or new concepts**. The team still decides **relevance** and **when the model changes**, and keeps the code consistent with the theory.

---

## Practice Q&A

1. What are the 5 ideas of git's mental model?<details><summary>Answer</summary>Stream of snapshots; local operations; data integrity (SHA-1, stored by content hash); git only adds data; 3 states (modified, staged, committed).</details>
2. Why do most git commands work offline? What is a remote?<details><summary>Answer</summary>The full history is in the local .git database. A remote is a shared server with the same functionality, which you push to and pull/clone from.</details>
3. Name the 3 states and the 3 sections. What does clone copy?<details><summary>Answer</summary>Modified, staged, committed; working tree, staging area (index), git directory. Clone copies the git directory.</details>
4. Plumbing vs porcelain?<details><summary>Answer</summary>Porcelain: user-level commands. Plumbing: low-level commands on the primitive objects and the 3 sections.</details>
5. You stage a file and then edit it again. What does status show and what is committed?<details><summary>Answer</summary>Both staged and modified; only the staged version is committed.</details>
6. Why is branching cheap? How many parents can a commit have?<details><summary>Answer</summary>A branch is just a pointer to a commit. 0 (initial), 1 (normal), 2+ (merge).</details>
7. What does `git checkout -b iss53` change in the graph? Which pointer moves on commit?<details><summary>Answer</summary>A new pointer iss53 at the current commit, and HEAD → iss53. On commit, iss53 moves because HEAD points to it.</details>
8. When does git refuse to switch branches?<details><summary>Answer</summary>When uncommitted changes conflict with the target branch; commit or stash first.</details>
9. Fast-forward vs three-way merge?<details><summary>Answer</summary>Fast-forward: the merged commit is a descendant, so the pointer just moves. Three-way: histories diverged; git uses both tips + the common ancestor to make a merge commit with 2+ parents.</details>
10. After the hotfix is merged into main, why doesn't iss53 have it?<details><summary>Answer</summary>iss53 branched before the fix; `git merge main` into iss53 brings it, or wait for iss53's merge into main.</details>
11. What is a merge conflict, and how is it resolved?<details><summary>Answer</summary>The same part of the same file changed in both branches. Git pauses, shows unmerged paths; fix manually, `git add` to mark resolved, commit to finish.</details>
12. When shouldn't you rebase?<details><summary>Answer</summary>When the commits are shared/pushed: rebase creates new commits. Use a three-way merge instead.</details>
13. What are the 4 key parts of `.git`?<details><summary>Answer</summary>objects, refs (branches, tags, remotes), HEAD (current branch), index (staging).</details>
14. What do `hash-object -w` and `cat-file -p / -t` do? Where is object `83baae61…` stored?<details><summary>Answer</summary>Hash and store content; print content / type. `.git/objects/83/baae61…` (2 + 38 chars).</details>
15. Why are trees needed, and what is in a tree entry?<details><summary>Answer</summary>Blobs have no file names. Entry: mode (100644 file, 100755 executable, 120000 symlink), type, hash, name.</details>
16. How do you build a tree and a commit with plumbing?<details><summary>Answer</summary>`update-index --add --cacheinfo` fills the index; `write-tree` writes it as a tree; `echo msg | commit-tree <tree> -p <parent>` makes the commit.</details>
17. What do `git add` + `git commit` do in plumbing terms?<details><summary>Answer</summary>Store blobs, update the index, write trees, write a commit pointing to the top tree and the previous commit.</details>
18. What is a branch at the plumbing level, and how is it created safely?<details><summary>Answer</summary>A file in .git/refs/heads with a commit hash; `git update-ref refs/heads/<name> <hash>`.</details>
19. What is a symbolic reference? How does commit use HEAD?<details><summary>Answer</summary>A ref pointing to another ref: HEAD = `ref: refs/heads/main`. The new commit's parent is the commit HEAD's branch points to. Use `git symbolic-ref`.</details>
20. Tag object vs commit vs branch?<details><summary>Answer</summary>Like a commit (tagger, date, message) but points to a commit, not a tree; like a branch but never moves.</details>
21. What is Naur's "theory", and what are his two cases?<details><summary>Answer</summary>Knowledge to do, explain, justify and answer questions. Group B broke A's compiler despite full docs; a 200k-line system's own team found faults outsiders couldn't.</details>
22. What are the theory's 3 capabilities, and when does a program "die"?<details><summary>Answer</summary>Relate to the world, justify the design, extend not patch. It dies when the team holding its theory dissolves.</details>
23. How do the two git users illustrate Naur?<details><summary>Answer</summary>The command user is group B (docs, stuck at surprises); the model holder derives behavior (cheap branches, fast-forward, recovery, conflicts).</details>
24. Theory vs spec?<details><summary>Answer</summary>A spec is an explicit snapshot of what; the theory is why, what's relevant, where it can stretch. Same spec + different theories → incompatible changes.</details>
25. Map Naur's capabilities to DDD, and name the UL's 3 jobs.<details><summary>Answer</summary>Model-driven design; arguing in domain terms; refactoring toward deeper insight. Transmission, detecting drift, binding code to theory.</details>
26. Bounded context in theory terms? Naur vs DDD? Use with AI agents?<details><summary>Answer</summary>The scope of one team's theory (context map relates them). Naur: inexpressible, no method; DDD: mostly explicit, patterns. Give agents the glossary, specs in its terms, reject synonyms; the team owns relevance and model changes.</details>
