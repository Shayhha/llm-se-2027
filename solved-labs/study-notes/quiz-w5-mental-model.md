# Quiz W5: the lecturer's mental model notes

**Based on:** `mental_model/Git Mental Model.md` and `mental_model/Mental Models of Software Projects.md`
(the lecturer's notes; most quiz questions should come from here). Same order as the files.

---

# Part A: Git Mental Model

## 1. The mental model (5 ideas)

| Idea | What it says |
|---|---|
| **Stream of snapshots** | every commit is a **picture of all your files** at that moment. If a file didn't change, git doesn't store it again, just a **link to the identical file** already stored |
| **Local operations** | the **full history is in a local database** (`.git`, from `git init` or clone), so most operations (e.g. browsing history) need no network. To share, you **push** to a server (e.g. GitHub) that has **the same functionality as a local git database**; you can pull or clone from it |
| **Data integrity by design** | everything is **checksummed (SHA-1) before it is stored** and referred to by that checksum: a **40-character hex** string. Git stores content **by the hash of its contents, not by file name**, so nothing can change without git knowing |
| **Git only adds data** | nearly every action **only adds** to the database; it is hard to make git erase anything. A committed snapshot is very hard to lose (especially if pushed), and you can **almost always undo** and restore any snapshot |
| **3 states** | **modified** (changed, not committed) · **staged** (marked to go into the next commit) · **committed** (safely stored in the local database) |

**The 3 sections of a project** (matching the 3 states):

| Section | What it is |
|---|---|
| **Working tree** | a **single checkout of one version**, pulled out of the compressed database onto disk for you to edit |
| **Staging area** | a **file in the git directory** recording what goes into the next commit; technical name: the **index** |
| **Git directory** (`.git`) | the metadata + **object database**; the most important part, and **what is copied when you clone** |

**Workflow:** git directory →(checkout)→ working tree →(stage fixes)→ staging area →(commit)→ git directory.
1. Modify files in the working tree.
2. **Selectively stage** only the changes you want in the next commit.
3. Commit: store the staged snapshot **permanently** in the git directory.

A version in the git directory = **committed**; changed and added = **staged**; changed since checkout but not staged = **modified**.

**Plumbing vs porcelain:**
- **Porcelain** = user-level convenient commands: branches, commits, tags, staging, copy/restore from a remote.
- **Plumbing** = low-level commands that manipulate the **primitive objects** of the database and the **3 sections**.

## 2. Porcelain view

**Creating a repository**, two ways:
- turn an existing local directory into a repo: `git init` → `git add *.c` → `git add LICENSE` → `git commit -m 'Initial project version'`;
- **clone** an existing repo from a remote server: `git clone https://github.com/melhadad/llm-se-2027.git`.

**Tracking files:** a file is **untracked**, **unmodified**, **modified** or **staged**:
- untracked →(add)→ staged;
- unmodified →(edit)→ modified →(stage)→ staged;
- staged →(commit)→ unmodified;
- unmodified →(remove)→ untracked.

**`git status`** shows the state: "nothing to commit, working tree clean"; a new file is listed under **"Untracked files"**; after `git add` it is under **"Changes to be committed: new file"**.
**Trap:** modify a file, stage it, then **modify it again**: the second change is **not staged**; the file appears **both** as staged and as modified. Also: `git rm`, `git mv`.

**Commit history:** `git log` lists commits of the current branch in **reverse chronological order**. Each commit has a message, author, date, a **SHA-1**, and a pointer to its **parent** commit (the snapshot it was built from).

**Remotes:** a repo can be linked to remote repos (**several** allowed) to **push** (send) and **fetch** (get) data. `git remote -v` lists them (e.g. `origin`).

**Tagging:** marks important points, typically **releases** (v1.0, v2.0). `git tag` lists; `git tag -a v1.4 -m "my version 1.4"` creates an annotated tag; `git show v1.4` shows the tagger, date, message and the commit.

## 3. Branching

**Branching** = diverging from the main line and working in **isolation** without disturbing it, e.g. a **feature branch** (later **merged** into main) or a **long-running branch** for a maintained version.

**Why it's cheap:** branches are **just pointers to commit objects**, so creating and switching is very fast.

**A commit object** holds a pointer to the **snapshot** you staged, the author's name and email, the message, and pointers to its **parent(s)**: **0** for the initial commit, **1** normally, **2+** for a merge.

**The scenario (`iss53` + hotfix):**

| Step | Command | Result in the graph |
|---|---|---|
| Start | (history C0 ← C1 ← C2) | `main` → C2, **HEAD → main** |
| Work on issue 53 | `git checkout -b iss53` (= `git branch iss53` + `git checkout iss53`) | a **new pointer** `iss53` → C2; HEAD → iss53. Nothing else changes |
| Commit on it | `git commit -a -m '...'` | C3; **iss53 moves forward** (because HEAD points to it); main stays at C2 |
| Urgent production bug | `git checkout main` | the working directory goes back to **exactly** main's last commit (git adds, removes and modifies files) |
| Hotfix | `git checkout -b hotfix` → edit → `git commit -a` | C4 on hotfix (parent C2) |
| Deploy the fix | `git checkout main` → `git merge hotfix` | **Fast-forward**: main → C4 |
| Clean up | `git branch -d hotfix` | the hotfix pointer is deleted (main points to the same place) |
| Back to work | `git checkout iss53` → edit → commit | C5 (parent C3). **C4's fix is not in iss53**: `git merge main` to get it, or wait until iss53 is merged |
| Finish the feature | `git checkout main` → `git merge iss53` | **three-way merge** → **C6** with parents C4 and C5; then `git branch -d iss53` |

**Before switching branches:** if uncommitted changes **conflict** with the branch you check out, **git won't let you switch**. Best to have a **clean working state** (commit, or **stash**).

**Fast-forward merge:** the commit you merge in is **directly ahead** of yours (reachable by following its history), so there's **no divergent work** and git **just moves the pointer forward**.

**Three-way merge:** histories **diverged**: your commit isn't an ancestor of the other. Git uses **3 snapshots**: the two branch tips and their **common ancestor** (C2), creates a **new snapshot** and a **merge commit** that has **more than one parent**.

**Merge conflicts:** the **same part of the same file** was changed differently in both branches.
- git **doesn't create the merge commit**; it **pauses** the merge;
- `git status` shows **"Unmerged paths"** / "both modified";
- the file shows `<<<<<<< HEAD` (your branch's version, above `=======`) and `>>>>>>> iss53` (the other branch's, below);
- resolve by choosing one side or combining them **manually** → **`git add`** marks it resolved → **commit** finalizes the merge.

**Rebasing:** a different strategy for a non-fast-forward integration (Pro Git "Git Branching – Rebasing"). In short: it **replays** your commits on top of the other branch as **new commits**, for a linear history. There are strict rules for when to use it: **don't rebase commits others already have** (pushed / shared); otherwise use a three-way merge.

## 4. Plumbing view

**`git init` creates `.git`**, whose key parts are:

| Part | Holds |
|---|---|
| **`objects`** | all the content of the database (every version of every file) |
| **`refs`** | pointers to commit objects: **branches, tags, remotes** |
| **`HEAD`** | points to the branch **currently checked out** |
| **`index`** | the staging area |

**Objects** encode the snapshots. Each is identified by a **40-character hash** derived from its content; git uses these hashes as **immutable pointers to immutable nodes in a graph** of objects. Types: **blob** (one file's content), **tree** (a folder: blobs and sub-trees), **commit** (refers to a snapshot tree); plus **tag**.

**Blobs and `hash-object` / `cat-file`:**
- `echo 'test content' | git hash-object --stdin` → prints the hash only (`--stdin` reads standard input); **`-w` actually writes** the object.
- Stored as **one file per piece of content**, named by the SHA-1 of the **content + a header**: folder = **first 2 characters**, file name = the **other 38**.
- `git cat-file -p <hash>` prints the content (figures out the type); **`-t`** prints the type (`blob`).
- **Versions:** hash-object `version 1`, then `version 2` → **two different blobs**; delete the file and restore either version with `cat-file -p <hash> > test.txt`. Blobs are **immutable**, which gives simple version control.
- Problem: you must remember hashes, and **no file name is stored**, only content → **trees**.

**Trees** store **file names** and group files, like a simplified **UNIX file system** (trees ≈ directories, blobs ≈ inodes/contents). Each entry = **mode, type, hash, name**:

```
$ git cat-file -p main^{tree}
100644 blob a906cb2a…  README
100644 blob 8f941393…  Rakefile
040000 tree 99f1a6d1…  lib
```

`main^{tree}` = the tree of main's last commit; `lib` is a **sub-tree**. Modes: **`100644`** normal file, **`100755`** executable, **`120000`** symbolic link (the only valid ones for blobs).

**Creating trees:** git writes trees **from the staging area (index)**:
- `git update-index --add --cacheinfo 100644 <hash> test.txt` puts an entry in the index (`--add`: not in the index yet; `--cacheinfo`: the content is in the database, not the directory);
- **`git write-tree`** writes the index out as a tree object and prints its hash (`cat-file -t` → `tree`);
- a second tree with test.txt **v2** + `new.txt` reuses the v2 blob's hash.

**Commit objects** solve the remaining problems: remembering tree hashes, and **who** saved a snapshot, **when** and **why**.
- `echo 'First commit' | git commit-tree d8329f` → a commit hash;
- `git cat-file -p` shows: `tree <hash>`, the **parent(s)** (none for the first), **author/committer** (from `user.name`, `user.email` + timestamp), a blank line, the **message**;
- `git commit-tree <tree> -p <parent>` chains commits; `git log --stat <last>` then shows a real history built **without any porcelain**.

**This is what `git add` + `git commit` do:** store blobs for changed files, update the index, write trees, write a commit pointing to the top tree and the previous commit. Each object is a separate file in `.git/objects`; following the pointers gives the **object graph** (commits → trees → blobs).

**References:** remembering hashes is impractical, so a **ref** stores a hash under a **simple name**, as a file in `.git/refs` (`refs/heads`, `refs/tags`).
- `echo <hash> > .git/refs/heads/main` works, but the **safe** way is **`git update-ref refs/heads/main <hash>`**;
- **a branch is just a pointer (reference) to the head of a line of work**: `git update-ref refs/heads/test cac0ca` creates a branch at the second commit, and `git log test` shows only that commit and earlier.

**HEAD:** how does `git branch <name>` know the last commit? Through HEAD. HEAD is a **symbolic reference**: it contains a pointer **to another reference**, not a hash: `cat .git/HEAD` → `ref: refs/heads/main`.
- `git checkout test` changes it to `ref: refs/heads/test`;
- `git commit` makes the new commit's **parent = the commit HEAD's ref points to**;
- the safe command is **`git symbolic-ref HEAD`** (read) / `git symbolic-ref HEAD refs/heads/test` (set).

**Tags:** the **4th object type**. A tag object is like a commit (tagger, date, message, pointer) but usually points to a **commit, not a tree**. Like a branch reference that **never moves**: a friendlier fixed name for one commit.

---

# Part B: Mental Models of Software Projects

## 5. Naur: programming as theory building (1985)

- The output of programming is mainly a **theory** the developers build about the **domain** the software works in: not mainly code and documents.
- "Theory" (from **Gilbert Ryle**) = knowledge that lets you **do something intelligently** and also **explain** it, **justify** it and **answer questions** about it.
- **Case 1:** group B extended a **compiler** written by group A, with **full source, extensive design documents and access to A**, and still proposed patches that "effectively destroyed the power and simplicity" of the system. A spotted them instantly: they saw facilities **already built into the structure** that B couldn't see, even though the documents discussed them.
- **Case 2:** the programmers of a **200,000-line real-time system** found faults using only their **own knowledge + the source code**; other teams with **complete documentation** kept hitting problems the original team cleared up easily.
- **Conclusion:** the theory "could not conceivably be expressed, but is inextricably bound to human beings". A program is **alive** while a team holding its theory controls it, and **dies** when that team is dissolved (even if it keeps running). Reviving it "merely from the documentation, is strictly impossible".

**What the theory lets programmers do that text cannot** (3 capabilities):
1. **Relate the program to the world:** which part of the world each part of the code corresponds to; decide what is **relevant**.
2. **Justify the design:** explain **why** each part is the way it is (from "direct, intuitive knowledge").
3. **Respond to change:** see how a new demand **resembles** something the program already does, so the change **extends the design instead of patching it**.

All 3 depend on **noticing similarities**, which Naur says **can't be written as rules** (like recognizing a face or a tune).
**Lecturer's note:** "system 1"-like AI makes that claim **less convincing**, but the idea of **theory as the key product** stands: "owning" a project = you can **explain** its relation to the domain, **justify** the design and **adapt** it to change.

## 6. The git example, and theory vs specs

**Two git users:**
- **user 1 knows the commands:** `add`, `commit`, `checkout -b`, `merge`;
- **user 2 holds the model:** history = a stream of snapshots, objects stored by **content hash**, git **only adds** data, files move between **3 states**, a branch is **just a pointer**.

User 2 can **derive** behavior never memorized:
- **branching is cheap** → it creates one pointer;
- **fast-forward** → the target is a **descendant** of the current commit, so the pointer just moves;
- a **"lost" commit is usually recoverable** → nothing was erased;
- a **merge conflict** → both branches changed the **same region relative to a common ancestor**.

User 1 is like **Naur's group B**: full documentation (the porcelain commands), stuck the moment something unexpected happens. A software project is the same, except the team must **build** the model first instead of reading it from a book. Code, specs, architecture and design all come **out of** the shared understanding; writing them is **how** the team builds the model, not the goal.

**Theory vs specs:**
- a **spec** = a finite, explicit set of statements about **what** the system must do (requirements, scenarios, interfaces, constraints): rules and criteria, exactly what Naur says a theory **can't be reduced to**;
- the spec is one **output** of the theory, a **snapshot** at one moment; the theory **produced** it and will produce the next one, keeping the project coherent;
- the theory = **why** these requirements and not others, which parts of the domain were judged **irrelevant**, what is **central vs incidental**, and **where the design can stretch**;
- **two teams with an identical spec but different theories will answer the next change request in incompatible ways.**

## 7. Theory, DDD and ubiquitous language

**DDD (Eric Evans, 2003)** offers **practices** to build the theory **on purpose**, share it across the team and keep code in line with it.

**Domain model as written-down theory:** a **deliberately selective abstraction** of what the team knows about the domain. It is **not a diagram or a document**: it is the **shared understanding** the diagrams point to (Naur's view, with documentation secondary). Built by **knowledge crunching**: developers + **domain experts** repeatedly work through **examples**, find **gaps** and **rebuild** the model.

**Naur's 3 capabilities ↔ DDD practices:**

| Naur: the theory lets you… | DDD practice |
|---|---|
| relate the program to the world, decide what's relevant | **Model-driven design:** code structure **mirrors the model** (each class/module = a domain concept); the model's selectivity = the relevance decision made explicit |
| justify why each part is the way it is | design choices argued **in domain terms** ("a Leg belongs to an Itinerary because…"), not technical terms |
| respond to change by extending, not patching | **Refactoring toward deeper insight:** when a requirement doesn't fit, **revise the model** instead of bolting on a special case |

**Ubiquitous language = the shared, visible part of the theory:** a **single vocabulary** used consistently in conversations with experts, specs, tests and **code identifiers**. A vocabulary is **not** a theory (knowing `commit`, `ref`, `HEAD` doesn't let you predict a fast-forward), but it does **3 jobs**:
1. **Transmission:** theory spreads only through close work with people who hold it; precise language in conversation supports that; newcomers learn by being **corrected** when they misuse a term.
2. **Detecting drift:** when an expert says "that sentence makes no sense", or a change request **can't be phrased naturally** in the language, the theory is being tested. Awkward phrasing = **early warning** that the change would be a **patch, not an extension** (Naur's decay).
3. **Binding code to theory:** when code names are the domain's terms, the mapping of text to world (capability 1) is partly **built into the code**.

Git's ubiquitous language: **blob, tree, commit, ref, HEAD, index, working tree**; each term precise, together the basis of the theory.

**Bounded contexts:** a model and its language hold only **inside** a bounded context; the same word ("Customer", "Order") can mean different things in **billing** vs **shipping**, and each context is usually owned by **one team**. A bounded context = **the scope of one team's theory**; a **context map** describes how different teams' theories relate.

**Where Naur and DDD differ:**
- **Can the theory be expressed?** Naur: fundamentally **no**. DDD: much of it **can** be made explicit (model, language, code), keeping the leftover judgment small. The "system 1" AI note leans the **same way as DDD**.
- **Method:** Naur: "there can be **no right method**". DDD is **patterns and principles, not an ordered procedure**, which Naur accepts as aids as long as the programmer decides when to use them.

## 8. Why this matters with AI agents

- The ubiquitous language is the **cheapest part of the theory to hand to an LLM**:
  - a **glossary** of domain terms in the agent's instructions;
  - specs **required to use those terms** (e.g. OpenSpec capability names `issue-enrichment`, `issue-routing` in the triage example);
  - **rejecting generated code** that brings in **synonyms or new concepts**.
- This lets the agent work **inside** the team's theory.
- The team stays responsible for what the language can't hold: deciding **what is relevant** and **when the model itself must change**, and for **preserving code integrity** with respect to the theory and maintaining **shared understanding**.

---

## Practice Q&A

1. What are the 5 ideas of git's mental model?<details><summary>Answer</summary>Stream of snapshots; local operations; data integrity (SHA-1 checksums, stored by content hash); git only adds data; 3 states (modified, staged, committed).</details>
2. What does "stream of snapshots" mean, and how is storage kept efficient?<details><summary>Answer</summary>Each commit is a picture of all files; unchanged files aren't stored again, only linked to the identical stored copy.</details>
3. Why can most git operations run without a network? What is a remote?<details><summary>Answer</summary>The full history is in the local .git database. A remote is a shared server with the same functionality as a local git database, which you push to and pull/clone from.</details>
4. How does git guarantee data integrity?<details><summary>Answer</summary>Everything is checksummed with SHA-1 (40 hex chars) before storage and referred to by that checksum; content is stored by hash, not by file name, so any change is detected.</details>
5. Why is it hard to lose data in git?<details><summary>Answer</summary>Nearly every action only adds data to the database; committed snapshots stay, so you can almost always undo and restore any snapshot.</details>
6. Name the 3 states and the 3 sections of a git project.<details><summary>Answer</summary>Modified, staged, committed; working tree, staging area (index), git directory.</details>
7. What is the staging area technically? What is copied by clone?<details><summary>Answer</summary>A file in the git directory called the index; clone copies the git directory (metadata + object database).</details>
8. Plumbing vs porcelain?<details><summary>Answer</summary>Porcelain: user-level commands (branches, commits, tags, staging, remotes). Plumbing: low-level commands on the primitive objects and the 3 sections.</details>
9. Two ways to create a repository?<details><summary>Answer</summary>`git init` in an existing directory (then add + commit), or `git clone <url>` of an existing remote repo.</details>
10. You modify a file, stage it, then modify it again. What does `git status` show, and what will commit include?<details><summary>Answer</summary>The file appears both as staged and as modified; commit includes only the staged version.</details>
11. What does a commit object contain? How many parents can it have?<details><summary>Answer</summary>A pointer to the snapshot tree, author/committer + email + timestamp, the message and parent pointer(s): 0 (initial), 1 (normal), 2+ (merge).</details>
12. Why is branching in git so cheap?<details><summary>Answer</summary>A branch is just a pointer to a commit; creating one writes one reference, nothing is copied.</details>
13. What does `git checkout -b iss53` do, and what changes in the graph?<details><summary>Answer</summary>Shorthand for `git branch iss53` + `git checkout iss53`. Only a new pointer iss53 to the current commit is created, and HEAD now points to iss53.</details>
14. You commit on iss53. Which pointer moves, and why?<details><summary>Answer</summary>iss53 moves to the new commit, because HEAD points to it; main stays.</details>
15. When does git refuse to switch branches?<details><summary>Answer</summary>When uncommitted changes in the working directory or staging area conflict with the branch being checked out. Commit or stash first.</details>
16. What happens to the working directory on `git checkout main`?<details><summary>Answer</summary>Git adds, removes and modifies files so it looks exactly like main's last commit.</details>
17. When is a merge a fast-forward?<details><summary>Answer</summary>When the commit being merged is directly ahead of (a descendant of) the current one; there is no divergent work, so git just moves the pointer.</details>
18. Describe a three-way merge.<details><summary>Answer</summary>Histories diverged; git uses the two branch tips and their common ancestor to create a new snapshot and a merge commit with more than one parent.</details>
19. After merging the hotfix into main, why doesn't iss53 contain the fix? How do you get it?<details><summary>Answer</summary>iss53 branched before the fix (C4 isn't its ancestor). Run `git merge main` on iss53, or wait until iss53 is merged into main.</details>
20. What is a merge conflict, and how is it resolved?<details><summary>Answer</summary>The same part of the same file changed differently in both branches. Git pauses (no merge commit), lists unmerged paths; edit the file, `git add` to mark it resolved, then commit to finish.</details>
21. In conflict markers, which part is HEAD's?<details><summary>Answer</summary>The part between `<<<<<<< HEAD` and `=======` is the checked-out branch's (e.g. main); below it, up to `>>>>>>> iss53`, is the merged branch's.</details>
22. When should you not rebase?<details><summary>Answer</summary>When the commits are already shared/pushed: rebase replaces them with new commits. Then use a three-way merge.</details>
23. What are the 4 key parts of `.git`?<details><summary>Answer</summary>objects (all content), refs (pointers to commits: branches, tags, remotes), HEAD (current branch), index (staging area).</details>
24. What do `git hash-object -w` and `git cat-file -p/-t` do?<details><summary>Answer</summary>hash-object computes the SHA-1 of content (+ header) and with -w stores it in .git/objects; cat-file -p prints an object's content, -t its type.</details>
25. Where is an object with hash `83baae61…` stored?<details><summary>Answer</summary>`.git/objects/83/baae61…`: folder = first 2 chars, file = the remaining 38.</details>
26. Why do we need tree objects? What does a tree entry contain?<details><summary>Answer</summary>Blobs store only content, no file names. A tree entry has a mode, type, hash and file name (blob or sub-tree).</details>
27. What are modes 100644, 100755 and 120000?<details><summary>Answer</summary>Normal file, executable file, symbolic link.</details>
28. How is a tree created at the low level?<details><summary>Answer</summary>Fill the index (`git update-index --add --cacheinfo <mode> <hash> <name>`), then `git write-tree` writes the index as a tree object.</details>
29. What problems does the commit object solve, and how is one created?<details><summary>Answer</summary>Remembering tree hashes and recording who, when and why. `echo msg | git commit-tree <tree> [-p <parent>]`.</details>
30. What do `git add` + `git commit` do in plumbing terms?<details><summary>Answer</summary>Store blobs for changed files, update the index, write trees, write a commit pointing to the top tree and the previous commit.</details>
31. What is a branch at the plumbing level? How do you create one safely?<details><summary>Answer</summary>A file in .git/refs/heads holding a commit hash: a pointer to the head of a line of work. `git update-ref refs/heads/<name> <hash>`.</details>
32. What is a symbolic reference? How does `git commit` use HEAD?<details><summary>Answer</summary>A ref pointing to another ref: HEAD = `ref: refs/heads/main`. The new commit's parent is the commit HEAD's branch points to. Read/set with `git symbolic-ref`.</details>
33. How does a tag object differ from a commit and from a branch?<details><summary>Answer</summary>Like a commit (tagger, date, message, pointer) but points to a commit, not a tree; like a branch but never moves.</details>
34. What does Naur mean by "theory"?<details><summary>Answer</summary>(After Ryle) knowledge that lets you do something intelligently and explain, justify and answer questions about it: the team's understanding of how the program handles part of the world.</details>
35. Describe Naur's two cases.<details><summary>Answer</summary>Group B, with full source, docs and access to A, still broke the compiler's design; A saw it at once. A 200k-line real-time system's team found faults from knowledge + code, while documented outsiders struggled.</details>
36. When is a program "alive" and when does it "die"?<details><summary>Answer</summary>Alive while a team holding its theory controls it; dead when that team dissolves, even if it keeps running. It can't be revived from documentation alone.</details>
37. What 3 capabilities does the theory give, and what do they depend on?<details><summary>Answer</summary>Relate the program to the world, justify the design, respond to change by extending not patching. They depend on noticing similarities, which can't be written as rules.</details>
38. What is the lecturer's note on Naur's claim?<details><summary>Answer</summary>"System 1"-like AI makes "can't be expressed" less convincing, but theory remains the key product: owning a project = explain, justify, adapt.</details>
39. How do the two git users illustrate Naur?<details><summary>Answer</summary>The command user is like group B (has the docs, stuck at surprises); the model holder derives behavior: cheap branches, fast-forward, recoverable commits, conflicts vs a common ancestor.</details>
40. Theory vs spec?<details><summary>Answer</summary>A spec is an explicit snapshot of what the system must do, one output of the theory. The theory is why, what's relevant/central, and where it can stretch. Same spec + different theories → incompatible answers to the next change.</details>
41. What is a domain model for Evans, and how is it built?<details><summary>Answer</summary>A deliberately selective abstraction of the team's domain knowledge: the shared understanding, not a diagram. Built by knowledge crunching with domain experts over examples.</details>
42. Map Naur's 3 capabilities to DDD practices.<details><summary>Answer</summary>World/relevance → model-driven design; justification → arguing in domain terms; change → refactoring toward deeper insight.</details>
43. What 3 jobs does the ubiquitous language do?<details><summary>Answer</summary>Transmission (newcomers corrected), detecting drift (awkward phrasing warns of a patch), binding code to theory (identifiers = domain terms).</details>
44. What is a bounded context in theory terms? A context map?<details><summary>Answer</summary>The scope of one team's theory, where a model's terms hold; a context map describes how different teams' theories relate.</details>
45. Where do Naur and DDD differ?<details><summary>Answer</summary>Expressibility: Naur says the theory can't be expressed; DDD makes much of it explicit. Method: Naur says no right method; DDD is patterns, not a procedure.</details>
46. How should a team use the ubiquitous language with AI agents, and what stays the team's job?<details><summary>Answer</summary>Glossary in instructions, specs using the terms, reject code with synonyms/new concepts. The team still decides relevance and when the model changes, and preserves code integrity with the theory.</details>
