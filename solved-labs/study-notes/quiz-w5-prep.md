# Quiz W5 prep: git internals + domain models

**Scope:** the W4 lecture, *"Domain models as cognitive theory; git worked example"* (from the
syllabus and the assigned reading, **Pro Git ch. 10**), plus Tuesday's lab once it's published.

**The one idea:** git = a **content-addressed object store** (blobs, trees, commits) + **refs**
(movable names) pointing into an **immutable DAG** of commits. Branch, reset, rebase, stash,
cherry-pick and reflog are all **derived** from these.

## 1. The object store

| Object | Stores | Points to |
|---|---|---|
| **blob** | a file's **content only** (no name, no permissions) | nothing |
| **tree** | a **directory**: entries of (mode, name, hash) | blobs and trees |
| **commit** | a **snapshot**: root tree + parent(s) + author, committer, message | its tree and parent(s) |
| **tag** (annotated) | tagger, date, message for one object | usually a commit |

- **Content-addressed:** an object's name = **SHA-1 of `"<type> <size>\0" + content`** (40 hex
  characters). Same content → same name. **Objects are immutable**: changes create new objects.
- **Stored** zlib-compressed at `.git/objects/ab/cdef…` (first 2 hex characters = the folder).
  `git gc` packs loose objects into **packfiles** (delta-compressed).
- **The DAG:** each commit points to its parent(s), and a merge has 2. A commit's hash covers its
  tree and parents, so **changing old history changes every later hash**.
- **Snapshots, not diffs:** each commit is a full tree, and unchanged files reuse the same blob.
  Diffs are computed on demand.
- **Renames aren't stored** (they're detected from similar content); **empty folders can't be
  tracked** (a tree only holds blobs and trees, hence `.gitkeep`).
- **Tree modes:** `100644` file · `100755` executable · `040000` directory · `120000` symlink.

## 2. The `.git` folder

| Entry | What it is |
|---|---|
| `HEAD` | where you are: `ref: refs/heads/main` (or a hash when detached) |
| `config` | the repository's settings (remotes, branches, user) |
| `index` | the **staging area**, a binary file: the proposed next commit |
| `objects/` | **all objects** (blobs, trees, commits, tags): loose files + `pack/` |
| `refs/heads/` | **branches**: one file per branch, holding a commit hash |
| `refs/tags/`, `refs/remotes/` | tags; remote-tracking branches (`origin/main`) |
| `logs/` | the **reflog**: the history of HEAD and branch positions |
| `hooks/` | scripts run on events (e.g. `pre-commit`) |
| `ORIG_HEAD` | HEAD before a reset, rebase or merge |
| `packed-refs` | refs packed into one file (a performance detail) |

The working directory is everything **outside** `.git`. Deleting `.git` deletes the repository
and its history.

## 3. Plumbing vs porcelain

**Porcelain** = user commands (`add`, `commit`, `merge`). **Plumbing** = the low-level commands
they're built on; the lab's mini git implements these:

| Command | Does |
|---|---|
| `git hash-object [-w] <file>` | file → blob hash (`-w` also writes the object) |
| `git cat-file -t / -s / -p <hash>` | an object's type / size / content |
| `git update-index --add <file>` | file → index |
| `git write-tree` | index → tree object |
| `git commit-tree <tree> -p <parent> -m msg` | tree → commit object |
| `git update-ref refs/heads/main <hash>` | move a branch |

**`git commit` = `write-tree` + `commit-tree`** (parent = HEAD) **+ `update-ref`** (move the branch).

## 4. Refs, HEAD and the three trees

- **A ref** = a **mutable name** for a commit (a file holding a hash). **A branch** = a movable
  pointer in `refs/heads/`; committing moves it forward.
- **HEAD** = the current position, normally a **symbolic ref** to a branch. **Detached HEAD** =
  HEAD holds a commit hash; new commits there belong to **no branch** (save them with
  `git switch -c <name>`).
- **Immutable objects, mutable refs:** only the pointers move, so almost everything can be
  recovered.
- **Tags:** lightweight = just a ref; annotated = a tag object the ref points to.
- **Revision syntax:** `HEAD~2` = 2 generations back · `HEAD^2` = the second parent of a merge ·
  `HEAD@{2}` = where HEAD was 2 moves ago (reflog).

| Tree | What it is |
|---|---|
| **HEAD** | the last commit on the current branch |
| **Index** (staging area) | the proposed next commit |
| **Working directory** | the files on disk |

| `git reset <commit>` | Branch | Index | Working dir | Result |
|---|---|---|---|---|
| `--soft` | ✓ | | | changes stay **staged** |
| `--mixed` (default) | ✓ | ✓ | | changes stay, **unstaged** |
| `--hard` | ✓ | ✓ | ✓ | changes **discarded** |

## 5. Derived commands

| Command | What it really does |
|---|---|
| **branch / tag** | create a ref (a moving one / a fixed one) |
| **merge** | **fast-forward** (just move the ref) or **three-way** (merge base + both tips → a commit with **2 parents**) |
| **rebase** | **replays** commits onto a new base as **new commits** (new hashes); the old ones remain |
| **cherry-pick** | copies **one commit's change** as a new commit |
| **revert** | a **new commit** that undoes an old one (safe on shared branches) |
| **stash** | saves uncommitted work as **commits** at `refs/stash`, then cleans the working dir |
| **reflog** | a **local** log of every HEAD and branch position |

**Rewriting shared history** (rebase, amend) is dangerous: others still have the old commits.

## 6. Disaster recovery

**A committed change is almost never lost.** The objects stay until `gc` (unreachable objects
about 2 weeks, reflog entries 90 days).

| Disaster | Recovery |
|---|---|
| Bad `reset --hard` | `git reflog` → find the hash → `git reset --hard <hash>` |
| Botched rebase | `git reflog` → the entry before it → `reset --hard` (or `ORIG_HEAD`) |
| Commits in detached HEAD | `git reflog` → `git branch rescue <hash>` |
| Deleted branch | the hash from `git reflog` → `git branch <name> <hash>` |
| Dropped stash | `git fsck --lost-found` finds **dangling** commits |

**Dangling** = no ref leads to it. **The reflog and index are local**, never pushed.

## 7. Remotes

**A remote is just another repository.**
- `fetch` downloads objects and updates **remote-tracking refs** (`origin/main`).
- `pull` = fetch + merge (or rebase).
- `push` uploads objects and moves the remote's branch.

A **refspec** maps remote refs to local ones (`refs/heads/*:refs/remotes/origin/*`). A clone has
the **full history**.

## 8. Domain models (DDD)

| Concept | Meaning |
|---|---|
| **Domain model as cognitive theory** | the model is the team's **theory of the program** (Naur, W1). When agents write the code, it must be written down and shared (glossary, invariants, specs) |
| **Why it matters now** | code is cheap; the shared model is the lasting asset |
| **Ubiquitous language** | one name per concept, everywhere; a machine-readable interface, since **naming measurably changes agent behaviour** |
| **Bounded context** | a boundary inside which one model and its terms are consistent; information hiding; managing an agent's context |
| **Anti-corruption layer** | a translation layer that keeps a foreign model out; here, insulation against **conventions an agent imports from its training data** |
| **Git as the example** | an **excellent model** (4 object types + refs) with **inconsistent commands**: `checkout` overloaded (branch, files, detach), `reset` with 3 modes, and **index = staging area = cache** |

## 9. Try it (Git Bash, throwaway folder; tested)

```bash
git init demo && cd demo && echo "hello world" > a.txt
git hash-object -w a.txt        # 3b18e512... → .git/objects/3b/18e512...
git cat-file -p 3b18e5          # hello world
git update-index --add a.txt && git write-tree          # → a tree hash
git commit-tree <tree> -m first                          # → a commit hash
git update-ref refs/heads/main <commit> && git log --oneline
git reset --hard HEAD~1 ; git reflog ; git reset --hard HEAD@{1}   # lose and recover
```

---

## Practice Q&A

1. What is the `.git` folder, and what are its main parts?<details><summary>Answer</summary>The repository itself: HEAD (the current position), config, index (staging), objects/ (all objects), refs/ (branches, tags, remotes), logs/ (the reflog), hooks/. Everything outside it is the working directory.</details>
2. What does "content-addressed" mean?<details><summary>Answer</summary>An object's name is the SHA-1 of its content (with a "type size\0" header), so the same content gives the same name and objects are immutable.</details>
3. Name the object types and what each stores.<details><summary>Answer</summary>Blob = file content; tree = directory (mode, name, hash); commit = root tree + parents + metadata; annotated tag = a named pointer with a message.</details>
4. Is a filename stored in the blob or the tree?<details><summary>Answer</summary>In the tree; a blob is pure content, so identical files are stored once.</details>
5. Does git store diffs or snapshots?<details><summary>Answer</summary>Snapshots (a full tree per commit, reusing unchanged blobs); diffs are computed on demand.</details>
6. Why can't old history be changed silently?<details><summary>Answer</summary>A commit's hash covers its tree and parents, so changing any old commit changes every later hash.</details>
7. Which plumbing steps make up `git commit`?<details><summary>Answer</summary>write-tree (index → tree), commit-tree (parent = HEAD), update-ref (move the branch).</details>
8. What do `hash-object` and `cat-file` do?<details><summary>Answer</summary>hash-object computes (and with -w writes) a blob; cat-file shows an object's type (-t), size (-s) or content (-p).</details>
9. What is a branch, physically?<details><summary>Answer</summary>A file in .git/refs/heads holding a commit hash: a movable pointer.</details>
10. What is HEAD, and what is a detached HEAD?<details><summary>Answer</summary>HEAD is the current position, normally a symbolic ref to a branch. Detached = it holds a commit hash, so new commits belong to no branch.</details>
11. What are the three trees?<details><summary>Answer</summary>HEAD (last commit), index (staging, the next commit), working directory (files on disk).</details>
12. reset --soft vs --mixed vs --hard?<details><summary>Answer</summary>All move the branch; soft keeps changes staged; mixed also resets the index (unstaged); hard also resets the files (discards).</details>
13. Merge (fast-forward vs three-way) vs rebase?<details><summary>Answer</summary>Fast-forward moves the ref; three-way uses the merge base and makes a 2-parent commit; rebase replays commits as new commits on a new base.</details>
14. Cherry-pick vs revert vs stash?<details><summary>Answer</summary>Cherry-pick copies one commit's change as a new commit; revert adds a commit undoing an old one; stash saves uncommitted work as commits at refs/stash.</details>
15. What is the reflog, and how do you recover a lost commit?<details><summary>Answer</summary>A local log of HEAD and branch positions. Find the hash in `git reflog`, then `git reset --hard <hash>` or `git branch <name> <hash>`.</details>
16. How do you undo a botched rebase?<details><summary>Answer</summary>`git reflog` → the entry before the rebase → `git reset --hard` it (or `ORIG_HEAD`).</details>
17. What is a dangling object, and when is it deleted?<details><summary>Answer</summary>An object no ref leads to; `git fsck` finds it, and `gc` deletes it after a grace period.</details>
18. `HEAD~2` vs `HEAD^2` vs `HEAD@{2}`?<details><summary>Answer</summary>Two generations back; the second parent of a merge; where HEAD was two moves ago.</details>
19. fetch vs pull vs push?<details><summary>Answer</summary>fetch updates origin/* only; pull = fetch + merge; push uploads and moves the remote's branch.</details>
20. Why can't git track an empty folder, and how are renames handled?<details><summary>Answer</summary>A tree only lists blobs and trees; renames aren't stored but detected from similar content.</details>
21. What does "domain model as cognitive theory" mean?<details><summary>Answer</summary>The model is the team's theory of the program (Naur); with agents writing code it must be made explicit and shared.</details>
22. What is ubiquitous language, and why is git a counterexample?<details><summary>Answer</summary>One name per concept, everywhere. Git's commands are inconsistent: `checkout` is overloaded, `reset` has 3 modes, index = staging area = cache.</details>
23. Bounded context vs anti-corruption layer?<details><summary>Answer</summary>A boundary where one model's terms are consistent; a translation layer that keeps a foreign model (or an agent's habits) out.</details>
