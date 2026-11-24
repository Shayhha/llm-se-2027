# Quiz W5: Git Mental Model

**Based on** the lecturer's `mental_model/Git Mental Model.md` (sections 1–5), plus the key points of
`Mental Models of Software Projects.md` (section 6).

## 1. The mental model of git

| Concept | Meaning |
|---|---|
| **Stream of snapshots** | Every commit stores a picture of all the project's files at that moment. A file that didn't change is not stored again; the commit links to the copy already stored. |
| **Local operations** | The whole history is stored on your machine in `.git`, so most commands (log, diff, commit) need no network. |
| **Remote** | Another git repository, usually on a server like GitHub, with the same functionality as yours. You **push** to send commits to it and **fetch / pull / clone** to get commits from it. |
| **SHA-1 hash** | A 40-character hex code calculated from content, e.g. `24b9da65…`. Git stores everything under the hash of its content, not under a file name. |
| **Data integrity** | Because every object is named by the hash of its content, changing even one byte gives a different hash. So nothing can change without git noticing. |
| **Git only adds data** | Almost every git command adds new data and doesn't delete old data. So committed work is very hard to lose and can almost always be restored. |

## 2. The three states and three sections

| Concept | Meaning |
|---|---|
| **Modified** | You changed the file, but haven't staged or committed the change. |
| **Staged** | You marked the file's current version to go into the next commit (`git add`). |
| **Committed** | The version is safely stored in the local database (`.git`). |
| **Working tree** | The project files on disk that you edit: one version taken out of the database. |
| **Staging area (index)** | A file inside `.git` that lists exactly what will go into the next commit. Its technical name is the **index**. |
| **Git directory (`.git`)** | The database of all objects and metadata. It is the most important part, and it is what `clone` copies. |
| **Basic workflow** | Edit files in the working tree → `git add` the changes you want → `git commit` stores that staged snapshot permanently. |
| **Porcelain** | The everyday user commands: `add`, `commit`, `checkout`, `branch`, `merge`, `push`, `tag`. |
| **Plumbing** | Low-level commands that work directly on git's objects and the index, e.g. `hash-object`, `write-tree`, `commit-tree`. |

## 3. Everyday commands (porcelain)

| Concept | Meaning |
|---|---|
| **`git init`** | Turns the current folder into a new, empty repository by creating `.git`. |
| **`git clone <url>`** | Copies an existing remote repository, with its full history, to your machine. |
| **Untracked file** | A new file git doesn't track yet; `git add` makes it tracked and staged. |
| **Unmodified file** | A tracked file that is the same as in the last commit. Editing it makes it modified. |
| **`git status`** | Shows which files are untracked, modified and staged. |
| **Edit after `add`** | If you stage a file and then edit it again, the new edit is **not** staged. Status shows the file as both staged and modified, and commit takes only the staged version. |
| **`git log`** | Lists the commits of the current branch, newest first, each with its hash, author, date and message. |
| **Parent commit** | The commit a new commit was built on. A commit has 0 parents if it's the first, 1 normally, and 2 or more if it's a merge. |
| **`git remote -v`** | Lists the remotes linked to the repository (e.g. `origin`). One repository can have several remotes. |
| **Tag** | A fixed name for one commit, usually a release such as `v1.4`. Unlike a branch, it never moves. `git tag -a v1.4 -m "msg"` creates an annotated tag. |

## 4. Branching and merging

| Concept | Meaning |
|---|---|
| **Branch** | A movable pointer to a commit; it lets you work in isolation without touching `main`. Creating one only creates a pointer, so it is instant. |
| **HEAD** | Points to the branch you are on now. When you commit, the branch that HEAD points to moves forward to the new commit. |
| **`git checkout -b iss53`** | Creates branch `iss53` and switches to it. It is shorthand for `git branch iss53` + `git checkout iss53`. |
| **`git checkout main`** | Switches to `main`: HEAD points to it and the files on disk change to match main's last commit. |
| **Switching is refused** | Git won't switch branches if your uncommitted changes conflict with the target branch. Commit or stash them first. |
| **Fast-forward merge** | When the branch you merge in is directly ahead of yours, git only moves your branch pointer forward. No new commit is created. |
| **Three-way merge** | When the two branches have diverged, git combines their two latest commits and their common ancestor. The result is a new **merge commit** with two parents. |
| **Common ancestor** | The last commit that both branches share, i.e. where they split. |
| **Merge conflict** | Both branches changed the same part of the same file. Git stops the merge and lists the file under "Unmerged paths" in `git status`. |
| **Conflict markers** | Between `<<<<<<< HEAD` and `=======` is your current branch's version; between `=======` and `>>>>>>> iss53` is the other branch's version. |
| **Resolving a conflict** | Edit the file to the correct content, run `git add` to mark it resolved, then `git commit` to finish the merge. |
| **`git branch -d <b>`** | Deletes a branch pointer after it was merged. The commits stay. |
| **Rebase** | Copies your commits onto the end of another branch as new commits, giving a straight-line history. Never rebase commits that others already have. |

**The lecture's scenario (`iss53` + hotfix):**

| Step | What happens |
|---|---|
| `git checkout -b iss53`, commit C3 | A new pointer `iss53` is created; it moves to C3, and `main` stays at C2. |
| Urgent bug: `git checkout main` | The files return to exactly main's version, without your iss53 work. |
| `git checkout -b hotfix`, commit C4 | The fix is made on its own branch, which starts at main (C2). |
| `git checkout main`, `git merge hotfix` | **Fast-forward**: main moves to C4. Then `git branch -d hotfix`. |
| `git checkout iss53`, commit C5 | iss53 does **not** contain the fix (C4); `git merge main` would bring it in. |
| `git checkout main`, `git merge iss53` | **Three-way merge** of C4 and C5 with their common ancestor C2 → merge commit C6. |

## 5. Inside `.git` (plumbing)

| Concept | Meaning |
|---|---|
| **`objects/`** | Stores all the content: every version of every file, plus all trees and commits. |
| **`refs/`** | Stores the pointers to commits: branches (`refs/heads`), tags (`refs/tags`) and remote branches. |
| **`HEAD` file** | Says which branch is checked out, e.g. `ref: refs/heads/main`. |
| **`index` file** | The staging area. |
| **Blob** | An object that stores the content of one file, without its name. Two versions of a file are two different blobs. |
| **Tree** | An object that stores a folder: each entry has a mode, a type (blob or tree), a hash and a file name. |
| **Commit object** | An object that stores a top-level tree's hash, the parent commit(s), the author and committer, and the message. |
| **Tag object** | A 4th object type: like a commit (tagger, date, message), but it points to a commit, not a tree. |
| **Object storage path** | An object is saved as `.git/objects/` + the first 2 hash characters (folder) + the other 38 (file name). |
| **File modes** | `100644` normal file, `100755` executable, `120000` symbolic link; `040000` marks a sub-tree. |
| **`git hash-object -w <file>`** | Computes the file's hash and, with `-w`, stores it as a blob. `--stdin` reads the content from standard input instead of a file. |
| **`git cat-file -p / -t <hash>`** | `-p` prints an object's content; `-t` prints its type (blob, tree, commit). |
| **`git update-index --add --cacheinfo`** | Adds an entry (mode, blob hash, file name) to the index by hand. |
| **`git write-tree`** | Writes the current index as a tree object and prints its hash. |
| **`git commit-tree <tree> -p <parent>`** | Creates a commit object for a tree, with an optional parent; the message comes from stdin. It does not move any branch. |
| **What `add` + `commit` do** | Store blobs for changed files and update the index, write trees from the index, then write a commit pointing to the top tree and the previous commit. |
| **Reference (ref)** | A file in `.git/refs` holding a commit's hash, so you can use a name instead of the hash. **A branch is exactly such a ref.** |
| **`git update-ref refs/heads/<b> <hash>`** | The safe way to create or move a branch to a commit. |
| **Symbolic reference** | A ref that points to another ref instead of a hash. HEAD is one: it contains `ref: refs/heads/main`. |
| **`git symbolic-ref HEAD`** | Reads which branch HEAD points to; with a ref argument, it sets it. |
| **How commit uses HEAD** | `git commit` makes the new commit's parent the commit that HEAD's branch points to, then moves that branch to the new commit. |

## 6. Mental models of software projects (Naur + DDD)

| Concept | Meaning |
|---|---|
| **Theory (Naur)** | The understanding a team builds of how the program handles part of the real world. It lets them explain the code, justify it and answer questions about it. |
| **Naur's evidence** | Group B had the full code, documents and access to group A, yet still damaged A's compiler design. The original team of a 200,000-line system found bugs that documented outsiders couldn't. |
| **Program life and death** | A program is "alive" while the team that holds its theory works on it. It "dies" when that team breaks up, and documentation alone can't revive it. |
| **3 capabilities of the theory** | Relate each part of the code to the world, justify why the design is the way it is, and handle changes by extending the design instead of patching it. |
| **Two git users** | One knows only the commands; the other knows the model (snapshots, pointers, only adds data). The second can work out behavior they never learned; the first is like Naur's group B, stuck at the first surprise. |
| **Theory vs spec** | A spec lists *what* the system must do at one moment; the theory knows *why*. Two teams with the same spec but different theories will make incompatible changes. |
| **Domain model (DDD)** | The team's shared, selective understanding of the domain, not a diagram. It is built by **knowledge crunching**: developers and domain experts work through examples together. |
| **Ubiquitous language** | One agreed name per concept, used in talk, specs, tests and code. Its 3 jobs: teach newcomers, warn when a change doesn't fit (drift), and tie code names to the theory. |
| **Bounded context** | The area where one model's terms have one meaning, usually owned by one team. The same word (e.g. "Customer") can mean something else in another context. |
| **Naur vs DDD** | Naur says the theory can't be written down; DDD says much of it can (model, language, code). |
| **With AI agents** | Give the agent a glossary of the terms (referenced from `AGENTS.md` / `CLAUDE.md`), and reject generated code that uses synonyms or new concepts. |

---

## Practice Q&A

1. What does "stream of snapshots" mean?<details><summary>Answer</summary>Each commit stores a picture of all files; unchanged files are linked to the stored copy, not stored again.</details>
2. Why do most git commands work without a network?<details><summary>Answer</summary>The full history is stored locally in `.git`.</details>
3. How does git make sure data isn't changed silently?<details><summary>Answer</summary>Everything is stored under the SHA-1 hash of its content, so any change gives a different hash.</details>
4. Why is it hard to lose committed work in git?<details><summary>Answer</summary>Almost every command only adds data and doesn't delete old data, so old versions can be restored.</details>
5. Name the 3 states of a file.<details><summary>Answer</summary>Modified, staged, committed.</details>
6. Name the 3 sections of a git project. Which one does clone copy?<details><summary>Answer</summary>Working tree, staging area (index), git directory. Clone copies the git directory.</details>
7. What is the staging area technically?<details><summary>Answer</summary>A file inside `.git` called the index, listing what goes into the next commit.</details>
8. Porcelain vs plumbing?<details><summary>Answer</summary>Porcelain = everyday user commands; plumbing = low-level commands on objects and the index.</details>
9. `git init` vs `git clone`?<details><summary>Answer</summary>init creates a new empty repository here; clone copies an existing remote repository with its history.</details>
10. You stage a file, then edit it again, then commit. What is committed?<details><summary>Answer</summary>Only the staged version; the second edit stays modified.</details>
11. How many parents can a commit have?<details><summary>Answer</summary>0 for the first commit, 1 normally, 2 or more for a merge commit.</details>
12. What is a branch, and why is creating one cheap?<details><summary>Answer</summary>A movable pointer to a commit; creating one just writes a pointer.</details>
13. What is HEAD?<details><summary>Answer</summary>A pointer to the current branch; on commit, that branch moves to the new commit.</details>
14. What does `git checkout -b iss53` do?<details><summary>Answer</summary>Creates branch iss53 at the current commit and switches to it (= `git branch` + `git checkout`).</details>
15. When does git refuse to switch branches?<details><summary>Answer</summary>When uncommitted changes conflict with the target branch; commit or stash first.</details>
16. When is a merge a fast-forward?<details><summary>Answer</summary>When the merged branch is directly ahead of yours, so git only moves your pointer forward.</details>
17. What is a three-way merge?<details><summary>Answer</summary>Merging diverged branches using both latest commits and their common ancestor, creating a merge commit with two parents.</details>
18. In the scenario, why doesn't iss53 contain the hotfix?<details><summary>Answer</summary>iss53 split off before the fix was made; `git merge main` into iss53 brings it in.</details>
19. What is a merge conflict?<details><summary>Answer</summary>Both branches changed the same part of the same file, so git stops and asks you to fix it.</details>
20. How do you resolve a conflict?<details><summary>Answer</summary>Edit the file, `git add` it to mark it resolved, then `git commit` to finish the merge.</details>
21. When should you not rebase?<details><summary>Answer</summary>When the commits are already shared with others, because rebase replaces them with new commits.</details>
22. What are the 4 key parts of `.git`?<details><summary>Answer</summary>objects (content), refs (branches, tags, remotes), HEAD (current branch), index (staging area).</details>
23. Blob vs tree vs commit?<details><summary>Answer</summary>Blob = one file's content; tree = a folder (names → blobs/trees); commit = a top tree + parents + author + message.</details>
24. Where is the object with hash `83baae61…` stored?<details><summary>Answer</summary>In `.git/objects/83/baae61…`: the first 2 characters are the folder.</details>
25. What do `hash-object -w` and `cat-file -p` do?<details><summary>Answer</summary>hash-object computes a hash and stores the content as a blob; cat-file -p prints an object by its hash.</details>
26. Why are tree objects needed?<details><summary>Answer</summary>Blobs store only content, so trees record the file names and folder structure.</details>
27. What do modes 100644, 100755 and 120000 mean?<details><summary>Answer</summary>Normal file, executable file, symbolic link.</details>
28. How do you build a commit with plumbing only?<details><summary>Answer</summary>`update-index` fills the index, `write-tree` turns it into a tree, `commit-tree` makes a commit from that tree.</details>
29. What do `git add` + `git commit` do internally?<details><summary>Answer</summary>Store blobs and update the index, write trees, and write a commit pointing to the top tree and the previous commit.</details>
30. What is a branch at the plumbing level?<details><summary>Answer</summary>A file in `.git/refs/heads` that holds a commit's hash; `git update-ref` sets it safely.</details>
31. What is a symbolic reference?<details><summary>Answer</summary>A ref that points to another ref: HEAD contains `ref: refs/heads/main`.</details>
32. How is a tag different from a branch?<details><summary>Answer</summary>A tag always points to the same commit; a branch moves forward with new commits.</details>
33. What is Naur's "theory"?<details><summary>Answer</summary>The team's understanding of how the program maps to the world, which lets them explain and justify it.</details>
34. What does Naur's group B example show?<details><summary>Answer</summary>Full code and documentation weren't enough: without the theory, B's changes damaged the design.</details>
35. What 3 things does the theory let a team do?<details><summary>Answer</summary>Relate code to the world, justify the design, and extend the design when things change instead of patching.</details>
36. Theory vs spec?<details><summary>Answer</summary>A spec says what the system must do; the theory knows why, so it guides the next change.</details>
37. What are the 3 jobs of the ubiquitous language?<details><summary>Answer</summary>Teach newcomers, warn when a change doesn't fit, and tie code names to the theory.</details>
38. How do you use the ubiquitous language with AI agents?<details><summary>Answer</summary>Give the agent a glossary of the terms and reject code that uses synonyms or new concepts.</details>
