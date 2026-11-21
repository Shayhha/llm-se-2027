# Quiz W5 prep: working with git + domain-driven design

**Scope:** the W4 lecture: everyday git (branches, workflows, fixing mistakes, handling a
production bug), the concepts behind git, and **DDD**. Plus Tuesday's lab once it's published.

---

## 1. How git works (just the concepts)

| Concept | Meaning |
|---|---|
| **Repository** | the project + its full history, stored in the hidden **`.git` folder** |
| **Commit** | a **snapshot** of the whole project at a moment, with a message, an author and a parent commit; identified by a **hash** |
| **Branch** | a **movable pointer** to a commit, i.e. a line of work. Creating one is instant and cheap |
| **HEAD** | **where you are now**, normally the current branch |
| **Detached HEAD** | you checked out a commit, not a branch; new commits there belong to no branch |
| **Working directory** | your files on disk |
| **Staging area (index)** | what goes into the **next commit** (`git add` puts changes here) |
| **Remote** (`origin`) | another copy of the repository, e.g. on GitHub |
| **Tag** | a fixed name for a commit, e.g. a release `v1.2.0` |

**The `.git` folder** holds everything:
- `objects/`: all commits, trees and file contents;
- `refs/`: branches and tags;
- `HEAD`: where you are;
- `index`: the staging area;
- `config`: settings and remotes;
- `logs/`: the reflog;
- `hooks/`: scripts run on events.

Delete it and the history is gone.

**Key facts:**
- commits are **snapshots, not diffs**;
- history **can't be changed silently**, because every commit's hash depends on its parent;
- a commit is **almost never truly lost**: `git reflog` remembers.

## 2. The everyday workflow

```bash
git clone <url>                 # copy a remote repository
git status                      # what changed? what is staged?
git add <file>                  # stage changes      (git add . = everything)
git commit -m "message"         # save a snapshot
git pull                        # get others' changes (= fetch + merge)
git push                        # send your commits to the remote
git log --oneline --graph       # see the history
git diff                        # unstaged changes  (git diff --staged = staged)
```

**`.gitignore`** lists files git must not track: build output, `.venv`, **`.env` with secrets**.

## 3. Branches

| Task | Command |
|---|---|
| **Create a branch and move into it** | `git switch -c feature/login` (older form: `git checkout -b feature/login`) |
| Create without moving | `git branch feature/login` |
| Move to an existing branch | `git switch main` (or `git checkout main`) |
| List branches | `git branch` (`-a` includes remote ones) |
| Delete a merged branch | `git branch -d feature/login` |
| Publish a new branch | `git push -u origin feature/login` |
| Merge a branch into the current one | `git switch main` → `git merge feature/login` |

**Why branches:** isolate work (a feature, a fix, an experiment) without breaking `main`, then
integrate it through a **pull request (PR)** with code review.

**Merge vs rebase:**

| | Merge | Rebase |
|---|---|---|
| What | joins two histories with a **merge commit** (or a **fast-forward** if there's nothing to join) | **replays** your commits on top of another branch, as **new** commits |
| History | true, but with extra merge commits | linear and clean |
| Rule | safe everywhere | **never rebase commits others already have** (shared or pushed branches) |

**Merge conflict:** both sides changed the same lines. Git marks them in the file:

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> feature
```

Fix the file → `git add <file>` → `git commit` (or `git rebase --continue`). Undo the attempt
with `git merge --abort`.

## 4. Scenario: a bug in production while you work on your own branch

You're on `feature/search` with **unfinished changes**, and production (`main`) has an urgent
bug:

1. **Save your unfinished work:** `git stash` (shelves the changes), **or** `git commit -m "WIP"`
   on your branch.
2. **Go to the production branch and update it:** `git switch main` → `git pull`
3. **Create a hotfix branch from it:** `git switch -c hotfix/login-crash`
4. **Fix, test, commit:** `git add …` → `git commit -m "Fix login crash"`
5. **Push and open a PR into `main`:** `git push -u origin hotfix/login-crash` → review → merge →
   deploy (often **tag** the release, e.g. `v1.2.1`).
6. **Return to your work:** `git switch feature/search` → `git stash pop` (if you stashed).
7. **Bring the fix into your branch too:** `git merge main` (or `git rebase main`, or
   `git cherry-pick <fix-commit>` for one commit).

**Why this way:**
- the hotfix starts from **what is actually in production**, not from your half-done feature;
- your unfinished work isn't mixed into the fix;
- the fix gets reviewed;
- your branch ends up with the fix too, so the bug doesn't come back when you merge.

## 5. Fixing mistakes

| Situation | Command | Note |
|---|---|---|
| Discard changes to a file (not staged) | `git restore <file>` | the changes are lost |
| Unstage a file (keep the changes) | `git restore --staged <file>` | |
| Fix the **last** commit's message or content | `git commit --amend` | rewrites the commit; don't if pushed |
| Undo the last commit, **keep** the changes | `git reset --soft HEAD~1` | staged · (`--mixed`: unstaged) |
| Undo the last commit and **throw away** the changes | `git reset --hard HEAD~1` | dangerous |
| Undo a commit that's **already pushed** | `git revert <hash>` | adds a new "undo" commit; **safe for shared branches** |
| Committed on the wrong branch | `git switch right-branch` → `git cherry-pick <hash>`, then remove it from the wrong branch | |
| "Lost" a commit (bad reset or rebase) | `git reflog` → `git reset --hard <hash>` | the reflog lists every place HEAD has been |
| Commits made in detached HEAD | `git switch -c save-it` (or find them in the reflog) | |

**Reset vs revert:**
- **reset** moves the branch back and **rewrites history**: local only;
- **revert** **adds** a commit that undoes the change, and history stays: safe after a push.

## 6. Branching strategies

| Strategy | Idea |
|---|---|
| **Feature branch + PR** | every change on its own branch → pull request → review → merge to `main` |
| **Git Flow** | `main` (production) · `develop` (integration) · `feature/*` · `release/*` · **`hotfix/*`** from `main` for urgent production bugs |
| **Trunk-based** | short-lived branches merged to `main` often (daily), guarded by CI and feature flags |

## 7. Git and the lecture's theme

- **A great model:** a few concepts (commits, branches as pointers, HEAD, remotes) explain
  everything else.
- **A poor *language*: a counterexample of ubiquitous language.**
  - `checkout` does unrelated things (switch branch, restore files, detach HEAD), which is why
    `switch` and `restore` were added;
  - `reset` has 3 modes;
  - **index = staging area = cache** (three names for one concept).

---

## 8. Domain-Driven Design (DDD)

**Domain model:** a shared model of the problem's concepts, rules and vocabulary.

**As cognitive theory:** it is the team's **theory of the program** (Naur, W1): how the code maps
to the world and why. **When code is cheap** (agents write it), this model is the lasting asset,
and it must be **written down** (glossary, invariants, specs), not kept only in people's heads.

| Concept | Meaning | Example (our triage system) |
|---|---|---|
| **Ubiquitous language** | **one agreed name per concept**, used by everyone: in talk, specs and code. For agents it's a machine-readable interface: **names change what they generate** | "severity" means only how bad a bug is; never "priority" (W1 Exercise B's `ticket_priority` broke this) |
| **Bounded context** | a boundary inside which a model and its terms are consistent; a term may mean something else in another context. Supports **information hiding** and keeps an **agent's context small** | "component" = a code folder in *routing*, but free text in *enrichment* |
| **Anti-corruption layer (ACL)** | a **translation layer** that converts an outside model into yours, so its concepts don't leak in. Here: insulation against **conventions an agent imports from its training data** | validating LLM output into our `TriageRecord` (rejecting "High", `feature-request`) |
| **Entity** | an object with an **identity** that persists while its data changes | an issue (repo + number) |
| **Value object** | defined only by its **values**, no identity, usually immutable | a severity level; a routing result |
| **Aggregate** | a cluster of objects changed together through one root, keeping **invariants** | a triage record with its rules (bugs have a severity) |
| **Invariant** | a rule that must always hold | "every security issue goes to the security queue" (W2) |

**Why DDD matters with AI agents:**
- agents **guess** whatever the model leaves unstated;
- inconsistent names lead to inconsistent code;
- a written glossary + invariants + clear boundaries give the agent the right context and catch
  conflicts (the W2 spec lab).

---

## Practice Q&A

1. How do you create a new branch and move into it?<details><summary>Answer</summary>`git switch -c <name>` (or `git checkout -b <name>`).</details>
2. What is a branch, and why are branches cheap?<details><summary>Answer</summary>A movable pointer to a commit (a small file holding a hash). Creating one copies nothing.</details>
3. You're on your feature branch with unfinished work, and production has an urgent bug. What do you do?<details><summary>Answer</summary>Stash or WIP-commit your work → `git switch main` → `git pull` → `git switch -c hotfix/x` → fix and commit → push and PR into main → merge and deploy (tag) → back to your branch (`git stash pop`) → `git merge main` to get the fix.</details>
4. Why create the hotfix from `main` and not from your feature branch?<details><summary>Answer</summary>main is what's in production; a branch off your feature would ship unfinished code with the fix.</details>
5. What does `git stash` do?<details><summary>Answer</summary>Shelves uncommitted changes and cleans the working directory; `git stash pop` brings them back.</details>
6. Merge vs rebase?<details><summary>Answer</summary>Merge joins histories with a merge commit (or fast-forward); rebase replays your commits on top as new commits for a linear history. Never rebase shared or pushed commits.</details>
7. What is a merge conflict, and how do you resolve it?<details><summary>Answer</summary>Both sides changed the same lines. Edit the marked file, `git add` it, then `git commit` (or abort with `git merge --abort`).</details>
8. fetch vs pull vs push?<details><summary>Answer</summary>fetch downloads without changing your branch; pull = fetch + merge; push sends your commits to the remote.</details>
9. Reset vs revert?<details><summary>Answer</summary>Reset moves the branch back (rewrites history, local only). Revert adds a commit that undoes a change (safe after a push).</details>
10. reset --soft vs --mixed vs --hard?<details><summary>Answer</summary>Soft keeps the changes staged; mixed (the default) keeps them unstaged; hard discards them.</details>
11. How do you recover a commit you "lost" with a bad reset?<details><summary>Answer</summary>`git reflog` → find the hash → `git reset --hard <hash>`.</details>
12. You committed to the wrong branch. Fix it.<details><summary>Answer</summary>Switch to the right branch and `git cherry-pick <hash>`, then remove the commit from the wrong branch (reset if not pushed, revert if pushed).</details>
13. What is the `.git` folder?<details><summary>Answer</summary>The repository: all objects (history), refs (branches, tags), HEAD, the index, config, the reflog and hooks. Deleting it deletes the history.</details>
14. What is HEAD, and what is a detached HEAD?<details><summary>Answer</summary>Your current position, usually a branch. Detached = pointing at a commit directly; new commits there belong to no branch.</details>
15. What is `.gitignore` for?<details><summary>Answer</summary>Files git must not track: build output, virtual environments, secrets like `.env`.</details>
16. Describe Git Flow and where hotfixes go.<details><summary>Answer</summary>main (production), develop (integration), feature/*, release/*; hotfix/* branches from main and merges back into main (and develop).</details>
17. Why is git a counterexample of ubiquitous language?<details><summary>Answer</summary>Its commands are inconsistent: `checkout` does several unrelated things, `reset` has three modes, and the staging area has three names (index, cache).</details>
18. What is a domain model, and why does it matter more when agents write code?<details><summary>Answer</summary>A shared model of the domain's concepts, rules and vocabulary: the team's theory of the program. Code is cheap, so the model is the lasting asset, and agents guess anything it leaves out.</details>
19. What is ubiquitous language? Give an example.<details><summary>Answer</summary>One agreed name per concept, used everywhere, including code. E.g. "severity" never called "priority"; inconsistent names make agents generate inconsistent code.</details>
20. What is a bounded context?<details><summary>Answer</summary>A boundary inside which one model and its terms are consistent; the same word may mean something else elsewhere. It limits what an agent needs to know.</details>
21. What is an anti-corruption layer? Give an example.<details><summary>Answer</summary>A translation layer that keeps an outside model out of yours. E.g. validating LLM output into a strict TriageRecord, so the model's conventions don't leak in.</details>
22. Entity vs value object?<details><summary>Answer</summary>An entity has an identity that persists while its data changes (an issue); a value object is defined only by its values (a severity level).</details>
