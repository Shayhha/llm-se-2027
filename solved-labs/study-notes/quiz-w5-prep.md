# Quiz W5 prep: git internals

**Scope:** the W4 lecture, *"Domain models as cognitive theory; git worked example"*, plus
Tuesday's lab (to be added when it is published). Built from the syllabus topics and the assigned
reading, **Pro Git, chapter 10 (Git Internals)**. The lecturer's own notes aren't public yet.

**The one idea:** git is a **content-addressed object store** (blobs, trees, commits) plus
**refs**: movable names pointing into an **immutable graph (DAG)** of commits. Every other
command (branch, reset, rebase, stash, cherry-pick, reflog) is **derived** from these few
concepts.

---

## 1. The object store

**Content-addressed:** every object is named by the **hash of its content** (SHA-1, 40 hex
characters).
- Same content → same name, so identical files are stored once.
- Change the content → a different name, so **objects are immutable**: nothing is edited, new
  objects are created.

| Object | Stores | Points to |
|---|---|---|
| **blob** | a file's **content only** (no name, no permissions) | nothing |
| **tree** | a **directory**: entries of (mode, name, hash) | blobs (files) and trees (sub-directories) |
| **commit** | a **snapshot**: one root tree + parent commit(s) + author, committer, message | its tree and its parent(s) |
| **tag** (annotated) | a name, a message and a tagger for one object | usually a commit |

**How an object is stored:**
1. Build a header: `"<type> <size>\0"`, e.g. `blob 12\0`.
2. Hash **header + content** with SHA-1. That hash is the object's ID.
3. Compress (zlib) and save at `.git/objects/<first 2 chars>/<other 38 chars>`.

`hello world\n` as a blob always has the same ID on every machine.

**History is a DAG** (directed acyclic graph): each commit points to its parent(s). A merge commit
has 2 parents. Because a commit's hash covers its tree and its parents, **changing any old commit
changes every hash after it**. History can't be silently altered.

**Loose objects vs packfiles:** new objects are stored one file each ("loose"); `git gc` packs
them into **packfiles** with delta compression.

## 2. Plumbing vs porcelain

- **Porcelain:** the friendly commands (`add`, `commit`, `checkout`, `merge`).
- **Plumbing:** the low-level commands they're built on. The lab builds a mini git from these.

| Command | Does |
|---|---|
| `git hash-object <file>` | computes a file's blob hash; with `-w`, also **writes** the blob to `.git/objects` |
| `git cat-file -t / -s / -p <hash>` | an object's **type** / **size** / **content** (pretty-printed) |
| `git update-index --add <file>` | puts a file into the **index** (staging area) |
| `git write-tree` | turns the current **index into a tree** object, printing its hash |
| `git commit-tree <tree> -p <parent> -m "msg"` | creates a **commit** object from a tree (+ parent) |
| `git update-ref refs/heads/main <hash>` | moves a branch to a commit |
| `git symbolic-ref HEAD refs/heads/main` | makes HEAD point to a branch |

**`git commit` in plumbing:** `write-tree` → `commit-tree` (parent = current HEAD) →
`update-ref` (move the branch to the new commit).

## 3. Refs and HEAD

- **A ref** is a **mutable name for a commit**: a small file containing a hash.
  - **branch:** `.git/refs/heads/main`
  - **tag:** `.git/refs/tags/v1.0`
  - **remote-tracking branch:** `.git/refs/remotes/origin/main`
- **A branch is just a movable pointer.** Creating one writes a 41-byte file. Committing moves the
  current branch forward to the new commit.
- **HEAD** is **where you are now**, normally a **symbolic ref** to a branch
  (`ref: refs/heads/main`).
- **Detached HEAD:** HEAD holds a **commit hash directly**, not a branch (e.g. after
  `git checkout <hash>`). New commits there belong to **no branch** and are easy to lose. Use
  `git switch -c <name>` to keep them.
- **Immutable DAG, mutable refs:** objects never change; only the refs move. That's why almost
  everything is recoverable.

## 4. The three trees

| "Tree" | What it is | Moved by |
|---|---|---|
| **HEAD** | the last commit on the current branch | `commit`, `reset`, `checkout` |
| **Index** (staging area) | the **proposed next commit** | `add`, `reset --mixed` |
| **Working directory** | your files on disk | editing, `checkout`, `reset --hard` |

**`git reset <commit>` moves the current branch, then optionally updates more trees:**

| Mode | Moves HEAD/branch | Resets the index | Resets the working dir | Effect |
|---|---|---|---|---|
| `--soft` | ✓ | | | undo commits, keep changes **staged** |
| `--mixed` (default) | ✓ | ✓ | | undo commits, keep changes **unstaged** |
| `--hard` | ✓ | ✓ | ✓ | **discard** the changes too (dangerous) |

## 5. Derived concepts (built from objects + refs)

| Command | What it really does |
|---|---|
| **branch** | create a new ref pointing to a commit |
| **merge** | a new commit with **two parents** (or a **fast-forward**: just move the ref) |
| **rebase** | **replays** your commits onto a new base, creating **new commits** (new hashes); the old ones still exist |
| **cherry-pick** | applies **one commit's change** as a **new commit** on the current branch |
| **reset** | moves the branch pointer (+ index / working dir) |
| **stash** | saves uncommitted work as **commits** referenced by `refs/stash`, then cleans the working dir |
| **revert** | a **new commit** that undoes an earlier one (history is kept; safe on shared branches) |
| **reflog** | a **local log of every position** HEAD and the branches have had |
| **tag** | a fixed (non-moving) name for a commit |

**Rewriting shared history is dangerous.** Rebase and amend create new commits; if others already
have the old ones, histories diverge.

## 6. Disaster recovery

**The rule:** a commit you made is **almost never lost**. It's still in `.git/objects` until
garbage collection (unreachable objects are kept for about 2 weeks; reflog entries for 90 days).

| Disaster | Recovery |
|---|---|
| **Bad `reset --hard`** | `git reflog` → find the old hash → `git reset --hard <hash>` |
| **Botched rebase** | `git reflog` → the entry before the rebase → `git reset --hard <hash>` (or `ORIG_HEAD`) |
| **Commits made in detached HEAD** | `git reflog` → `git branch rescue <hash>` |
| **Deleted a branch** | `git reflog` (or the hash printed on delete) → `git branch <name> <hash>` |
| **Lost stash** | `git fsck --lost-found` finds dangling commits |

- **`ORIG_HEAD`:** where HEAD was before a "dangerous" operation (reset, rebase, merge).
- **The reflog is local:** it isn't pushed, and every clone has its own.

## 7. Remotes

- **A remote** is **just another repository** (a URL with a name, e.g. `origin`).
- **`fetch`:** download objects and update the **remote-tracking refs** (`origin/main`). Your
  branches don't change.
- **`pull`** = `fetch` + `merge` (or rebase).
- **`push`:** upload objects and move the **remote's** branch.

## 8. DDD: domain models (the other half of the lecture)

| Concept | Meaning |
|---|---|
| **Domain model** | a shared model of the problem's concepts and rules; valuable when **code is cheap** (agents write code; the model is what persists) |
| **Ubiquitous language** | one agreed name per concept, used in talk, specs and code; **naming measurably changes agent behaviour** |
| **Bounded context** | a boundary inside which a model and its terms are consistent; links to **information hiding** and to **managing an agent's context** |
| **Anti-corruption layer** | a translation layer that keeps a foreign model out of yours; reinterpreted as **insulation against conventions an agent imports from its training data** |

**Git as the course's example:**
- its **internal model is excellent**: 4 object types + refs explain everything;
- its **command language is a counterexample of ubiquitous language**:
  - `checkout` does several unrelated things (switch branch, restore files, detach HEAD), which
    is why `switch` and `restore` were added later;
  - `reset` has three modes with very different effects;
  - the same thing has **three names**: index = staging area = cache.

---

## 9. Hands-on practice (in a throwaway folder)

Run it in **Git Bash**. PowerShell's `echo` writes a different encoding, so the hashes would
differ. Tested: `hello world` → blob `3b18e512…`.

```bash
mkdir gitlab && cd gitlab && git init
echo "hello world" > a.txt
git hash-object a.txt          # prints the blob hash (same on every machine)
git hash-object -w a.txt       # also writes it into .git/objects
find .git/objects -type f      # .git/objects/3b/18e5... : 2 chars / 38 chars
git cat-file -t 3b18e5         # blob
git cat-file -p 3b18e5         # hello world
git update-index --add a.txt   # stage it
git write-tree                 # prints a tree hash
git cat-file -p <tree>         # 100644 blob 3b18e5...  a.txt
git commit-tree <tree> -m "first"     # prints a commit hash
git update-ref refs/heads/main <commit>   # now `git log` shows it
cat .git/HEAD                  # ref: refs/heads/main
```

**Disaster drill:**

```bash
echo two > b.txt && git add b.txt && git commit -m two
git reset --hard HEAD~1        # "lose" the commit
git reflog                     # find "commit: two"
git reset --hard HEAD@{1}      # it's back
```

---

## Practice Q&A

1. What does "content-addressed" mean in git?<details><summary>Answer</summary>Every object is named by the hash of its content, so identical content has the same name, and changing content gives a new object. Objects are immutable.</details>
2. Name git's object types and what each stores.<details><summary>Answer</summary>Blob: a file's content (no name). Tree: a directory, i.e. (mode, name, hash) entries pointing to blobs and trees. Commit: a root tree + parent(s) + author and message. (Annotated tag: a named pointer with a message.)</details>
3. Where is a filename stored: in the blob or the tree? Why?<details><summary>Answer</summary>In the tree. A blob is pure content, so the same content under two names is stored once.</details>
4. How is an object's hash computed and stored?<details><summary>Answer</summary>SHA-1 of the header "type size\0" + the content; the result is zlib-compressed and saved at .git/objects/xx/yyyy… (the first 2 hex characters form the folder).</details>
5. Why can't history be changed silently?<details><summary>Answer</summary>A commit's hash covers its tree and its parents' hashes, so changing any old commit changes every hash after it.</details>
6. Plumbing vs porcelain: give two plumbing commands and what they do.<details><summary>Answer</summary>Porcelain = user commands; plumbing = low-level ones. `hash-object` hashes or writes a blob; `cat-file` reads an object; `write-tree` index → tree; `commit-tree` tree → commit.</details>
7. Which plumbing steps does `git commit` perform?<details><summary>Answer</summary>write-tree (index → tree), commit-tree (with the current HEAD as parent), and update-ref (move the branch to the new commit).</details>
8. What is a branch, physically?<details><summary>Answer</summary>A file under .git/refs/heads containing a commit hash: a movable pointer. Committing moves it forward.</details>
9. What is HEAD? What is a detached HEAD, and what is its risk?<details><summary>Answer</summary>HEAD is where you are: normally a symbolic ref to a branch. Detached = HEAD holds a commit hash directly; new commits belong to no branch and can be lost when you switch away.</details>
10. What are the three trees?<details><summary>Answer</summary>HEAD (the last commit), the index (staging area: the proposed next commit) and the working directory (the files on disk).</details>
11. reset --soft vs --mixed vs --hard?<details><summary>Answer</summary>All move the branch. Soft keeps the changes staged; mixed (the default) also resets the index, so changes are unstaged; hard also resets the working directory, discarding the changes.</details>
12. Merge vs rebase?<details><summary>Answer</summary>Merge creates a commit with two parents (or fast-forwards the ref). Rebase replays commits onto a new base as new commits with new hashes; the old commits remain until gc.</details>
13. What does cherry-pick do?<details><summary>Answer</summary>Applies one commit's change as a new commit on the current branch.</details>
14. What is the reflog, and how do you recover a lost commit?<details><summary>Answer</summary>A local log of every position HEAD and the branches had. Find the hash in `git reflog`, then `git reset --hard <hash>` or `git branch <name> <hash>`.</details>
15. How do you undo a botched rebase?<details><summary>Answer</summary>`git reflog` → the entry before the rebase → `git reset --hard <hash>`, or `git reset --hard ORIG_HEAD`.</details>
16. Why are "lost" commits usually recoverable?<details><summary>Answer</summary>Objects are immutable and stay in .git/objects; only refs moved. They are removed only by garbage collection after a grace period.</details>
17. fetch vs pull vs push?<details><summary>Answer</summary>fetch downloads objects and updates the remote-tracking refs (origin/main); pull = fetch + merge (or rebase); push uploads objects and moves the remote's branch.</details>
18. Revert vs reset?<details><summary>Answer</summary>Revert adds a new commit that undoes an old one (history kept, safe on shared branches); reset moves the branch pointer (rewrites history).</details>
19. What is ubiquitous language, and why is git's command set a counterexample?<details><summary>Answer</summary>One agreed name per concept, used everywhere. Git's commands are inconsistent: `checkout` does several unrelated things, `reset` has three very different modes, and the index is also called the staging area and the cache.</details>
20. What is a bounded context, and what is an anti-corruption layer?<details><summary>Answer</summary>A boundary within which one model and its terms are consistent; a translation layer that keeps a foreign model out of yours (in the course: protection against conventions an agent brings from its training data).</details>
