# Quiz W5 cheat sheet: git internals

**Git = a content-addressed object store + refs (movable names) pointing into an immutable DAG of
commits.**

**Objects**

| | |
|---|---|
| **Content-addressed** | object name = SHA-1 of `"type size\0" + content`; immutable |
| **Storage** | zlib-compressed at `.git/objects/ab/cdef…` (2 + 38 hex characters); `gc` → packfiles |
| **blob** | file content only (no name) |
| **tree** | directory: (mode, name, hash) → blobs and trees |
| **commit** | root tree + parent(s) + author + message; a merge has 2 parents |
| **DAG** | commit hashes cover parents, so changing old history changes every later hash |

**Plumbing**

| | |
|---|---|
| `hash-object [-w]` | file → blob hash (`-w` writes it) |
| `cat-file -t/-s/-p` | an object's type / size / content |
| `update-index --add` | file → index |
| `write-tree` | index → tree |
| `commit-tree <tree> -p <parent>` | tree → commit |
| `update-ref` | move a branch |
| **`git commit`** | = write-tree + commit-tree + update-ref |

**Refs and trees**

| | |
|---|---|
| **Branch** | a file in `refs/heads/` holding a commit hash: a movable pointer |
| **HEAD** | where you are; `ref: refs/heads/main` |
| **Detached HEAD** | HEAD = a commit hash; new commits belong to no branch |
| **Three trees** | HEAD (last commit) · index (next commit) · working directory (files) |
| **reset --soft / --mixed / --hard** | move the branch / + reset the index / + reset the files |

**Derived commands**

| | |
|---|---|
| **merge** | a commit with 2 parents, or a fast-forward (move the ref) |
| **rebase** | replay commits as **new** commits on a new base |
| **cherry-pick** | copy one commit's change as a new commit |
| **revert** | a new commit undoing an old one (safe on shared branches) |
| **stash** | uncommitted work saved as commits at `refs/stash` |
| **reflog** | local log of every HEAD and branch position |

**Recovery:** `git reflog` → find the hash → `git reset --hard <hash>` or `git branch rescue <hash>`.
`ORIG_HEAD` = before reset, rebase or merge. Commits stay until gc.

**Remotes:** another repository · **fetch** updates `origin/main` · **pull** = fetch + merge ·
**push** moves the remote's branch.

**DDD**

| | |
|---|---|
| **Ubiquitous language** | one name per concept everywhere; naming changes agent behaviour |
| **Bounded context** | a consistent model inside a boundary; manages context |
| **Anti-corruption layer** | translation that keeps foreign or agent-imported conventions out |
| **Git counterexample** | great model, inconsistent commands: `checkout` overloaded, 3 `reset` modes, index = staging area = cache |
