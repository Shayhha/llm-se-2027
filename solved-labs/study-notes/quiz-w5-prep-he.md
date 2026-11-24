# הכנה לבוחן 5: מושגי git + תכנון מונחה-תחום (DDD)

**מקורות:** קבצי המרצה `mental_model/Git Mental Model.md` ו-`Mental Models of Software Projects.md` + הסילבוס.

**היקף (סילבוס, שבוע 4):** עקרונות DDD ו**חקר המקרה של git**: מושגי היסוד של git, הפקודות שנגזרות מהם,
ו-git כדוגמה נגדית לשפה אחידה (ubiquitous language). בנוסף **המעבדה של יום שלישי** (mini git +
התאוששות מאסונות, ראו סעיף 8). הפקודות מופיעות בצורה הקלאסית (`checkout`, `reset`), כפי שהוצגו בכיתה.

---

## 1. המודל של git: מושגי היסוד

git הוא **מאגר אובייקטים מבוסס-תוכן** (content-addressed object store) ועוד כמה **מצביעים** לתוכו.

**המודל המנטלי של git לפי המרצה (5 רעיונות):**
1. **רצף של תמונות מצב (stream of snapshots):** כל commit הוא תמונה של כל הקבצים; קבצים שלא השתנו הם רק קישור לעותק שכבר נשמר.
2. **פעולות מקומיות:** כל ההיסטוריה נמצאת במסד הנתונים המקומי (`.git`), ולכן רוב הפקודות לא צריכות רשת. remote (GitHub) הוא אותו סוג של מסד נתונים, משותף לצוות.
3. **שלמות נתונים מובנית:** כל דבר מקבל **checksum (SHA-1, 40 תווי hex)** לפני שהוא נשמר, ומזוהה לפיו; התוכן נשמר לפי hash, **לא לפי שם קובץ**. שום דבר לא משתנה בלי ש-git יידע.
4. **git רק מוסיף מידע:** כמעט כל פעולה מוסיפה למסד, ולכן כמעט הכול ניתן לביטול.
5. **שלושה מצבים:** קובץ הוא **modified** (שונה), **staged** (מוכן ל-commit) או **committed** (נשמר).

| מושג | משמעות |
|---|---|
| **מבוסס-תוכן (Content-addressed)** | כל אובייקט נשמר תחת **ה-hash (SHA-1) של התוכן שלו**. אותו תוכן ← אותו hash; שינוי של בית אחד ← hash חדש. ה-hash הוא גם **השם** וגם **בדיקת שלמות** |
| **Blob** | **התוכן של קובץ אחד** (בלי שם, בלי תאריך) |
| **Tree** | **רשימת תיקייה**: שמות ← hash של blob (קבצים) ו-hash של tree (תת-תיקיות) |
| **Commit** | מצביע על **tree שורש אחד** (תמונת המצב המלאה) + **commit(s) הורה** (0 ל-commit הראשון, 1 בדרך כלל, 2+ למיזוג) + מחבר, committer, תאריך, הודעה |
| **DAG של commits** | כל commit מצביע אחורה להוריו, ונוצר **גרף מכוון חסר מעגלים**. האובייקטים **בלתי ניתנים לשינוי** (immutable): "שינוי" היסטוריה יוצר commits חדשים |
| **Ref** | **מצביע משתנה** (שם ← hash של commit, קובץ קטן ב-`.git/refs/`) לתוך ה-DAG הקבוע. **Branch** הוא ref ש**מתקדם** בכל commit (ולכן יצירה שלו מיידית); **tag** לא זז לעולם (`v1.2.0`) |
| **HEAD** | **איפה אתה נמצא**: בדרך כלל מצביע על branch (`ref: refs/heads/main`) |
| **Detached HEAD** | HEAD מצביע **ישירות על commit** ולא על branch; commits חדשים שם לא שייכים לאף branch |
| **Remote** | **מאגר אחר** (למשל `origin` ב-GitHub). `origin/main` = העותק האחרון שידוע לך של ה-branch שלו; `fetch` / `push` מעתיקים אובייקטים ומעדכנים refs |

**שלושת העצים / האזורים (the three trees):** **HEAD** (ה-commit האחרון) · ה-**index** / אזור ההכנה, staging area
(מה ייכנס ל-commit הבא) · **תיקיית העבודה**, working directory (הקבצים בדיסק).
`add` = תיקיית עבודה ← index; `commit` = index ← commit חדש + ה-branch מתקדם;
`checkout` = commit ← index + תיקיית עבודה.
- **Working tree:** checkout אחד של גרסה אחת, שנפרס מהמסד. **Staging area:** קובץ בתוך `.git` (השם הטכני: **index**). **Git directory:** המטא-דאטה + מסד האובייקטים, החלק החשוב ביותר, ו**מה שמועתק ב-clone**.
- **מחזור חיים של קובץ:** **untracked** ←(add)← **staged**; **unmodified** ←(עריכה)← **modified** ←(add)← **staged** ←(commit)← **unmodified**; מחיקה ← untracked.
- עורכים קובץ, עושים `add`, ועורכים שוב: **השינוי השני לא ב-staging**; הקובץ מופיע גם כ-staged וגם כ-modified.

**תיקיית `.git`** היא המאגר עצמו: `objects/` (blobs, trees, commits), `refs/` (branches, tags,
branches מרוחקים), `HEAD`, `index`, `config`, `logs/` (ה-reflog), `hooks/`. מוחקים אותה, וההיסטוריה
נעלמת; הקבצים בדיסק נשארים.

**השלכות:** commits הם **תמונות מצב (snapshots), לא הפרשים (diffs)** (קבצים שלא השתנו משתמשים באותו
blob); אי אפשר **לשנות היסטוריה בשקט** (ה-hash כולל את ה-tree ואת ההורים); אובייקטים רק **מתווספים**, ולכן
commit "אבוד" שורד עד ה-garbage collection, וה-**reflog** מוצא אותו.

## 2. מושגים נגזרים: כל השאר בנוי מהמודל

הנקודה בסילבוס: stash, rebase, reset, cherry-pick וה-reflog הם **לא מושגים חדשים**, אלא פעולות על
אובייקטים ו-refs.

| פקודה | במונחי המודל |
|---|---|
| **`git stash`** | שומר את השינויים שלא נשמרו **כ-commits** (שה-ref `refs/stash` מצביע עליהם), ואז מחזיר את תיקיית העבודה וה-index ל-HEAD |
| **`git reset <commit>`** | **מזיז את ה-ref של ה-branch הנוכחי** ל-`<commit>`. `--soft`: רק ה-ref; `--mixed` (ברירת מחדל): ref + index; `--hard`: ref + index + תיקיית עבודה |
| **`git cherry-pick <c>`** | לוקח את **השינוי** ש-`<c>` הכניס (ההפרש מול ההורה שלו) ויוצר איתו **commit חדש** על ה-branch הנוכחי (hash חדש) |
| **`git rebase <base>`** | עושה cherry-pick ל-commits שלך אחד-אחד על `<base>`, ואז **מזיז את ה-ref של ה-branch** ל-commit החדש האחרון. ה-commits הישנים עדיין קיימים, בלי ref |
| **`git merge <b>`** | **fast-forward:** אם ה-commit שממזגים הוא **צאצא** של שלך (אין עבודה מתפצלת), git רק **מזיז את המצביע**. **Three-way merge:** אם ההיסטוריות התפצלו, git משלב את שני הקצוות ואת **האב המשותף** (common ancestor) לתמונת מצב חדשה ו-**merge commit** (2 הורים) |
| **`git reflog`** | **יומן של כל ערך ש-HEAD (וכל branch) הצביע עליו**, מקומי בלבד. מכיוון ש-commits לא נמחקים, הוא משחזר כל מה ש-reset או rebase "איבדו" |
| **`git revert <c>`** | **commit חדש** עם השינוי ההפוך; שום דבר לא נכתב מחדש |

## 3. פקודות בסיסיות

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

- `init`: יוצר מאגר **חדש וריק** (תיקיית `.git/`) בתיקייה הנוכחית. `clone`: מעתיק מאגר **קיים** עם כל ההיסטוריה.
- `status`: מה השתנה ומה ב-staging. `add`: מעביר ל-staging. `commit`: שומר תמונת מצב, וה-branch מתקדם.
- `log`: ההיסטוריה (`--graph --all` מציג את ה-DAG). `diff`: שינויים שלא ב-staging (`--staged`: שכבר ב-staging).
- `fetch`: מביא אובייקטים מה-remote. `pull` = `fetch` + `merge`. `push`: שולח commits ומעדכן את ה-ref המרוחק.
- `remote add origin <url>`: מחבר את המאגר למאגר אחר.

**`.gitignore`** מפרט מה git לא יעקוב אחריו: תוצרי build, `.venv`, **`.env` עם סודות**.

**`git checkout`** (הפקודה ה"עמוסה"):

| צורה | מה עושה |
|---|---|
| `git checkout <branch>` | **מעבר** ל-branch (HEAD ← אותו branch; הקבצים מתעדכנים) |
| `git checkout -b <new>` | **יצירת branch ומעבר אליו** |
| `git checkout <commit>` | מעבר ל-commit ישן ← **detached HEAD** |
| `git checkout -- <file>` | **מחיקת** שינויים שלא נשמרו בקובץ (מעתיק אותו מה-index) |
| `git checkout <branch> -- <file>` | לקחת את הגרסה של קובץ מ-branch אחר |

git **מסרב לעבור branch** אם שינויים שלא נשמרו יידרסו: קודם commit או stash.

**`git stash`:** מדף (shelve) את השינויים שלא נשמרו (`-u`: כולל קבצים חדשים, untracked) · `stash list`
(מחסנית: `stash@{0}`, `{1}`…) · **`pop`** = מחיל מחדש **ומוחק** · **`apply`** = מחיל מחדש **ומשאיר** ·
`drop` / `clear` = מחיקת אחד / הכול. מקומי בלבד; `pop` יכול לגרום ל-conflict.

**ביטול פעולות:** הוצאה מ-staging `git reset HEAD <file>` · תיקון ה-commit האחרון `git commit --amend`
(לא אחרי push) · ביטול ה-commit האחרון `git reset --soft HEAD~1` · ביטול commit **שכבר נדחף**
`git revert <hash>`.

## 4. Branches, מיזוג, התנגשויות

**יצירת branch ומעבר אליו: `git checkout -b feature/login`** · יצירה בלבד `git branch x` · מעבר
`git checkout main` · רשימה `git branch -a` · מחיקה `git branch -d x` · פרסום `git push -u origin x` ·
מיזוג לתוך ה-branch הנוכחי `git checkout main` ← `git merge x`.

**Merge מול rebase:** merge שומר היסטוריה אמיתית (commit עם 2 הורים); rebase נותן היסטוריה ליניארית
(commits שנכתבו מחדש). כלל: **לעולם לא לעשות rebase ל-commits שיש כבר לאחרים**.

**התנגשות (conflict):** שני ה-branches שינו **אותו חלק באותו קובץ** ביחס לאב המשותף. git **עוצר** את המיזוג (בלי merge commit); `git status` מציג **unmerged paths** ("both modified"); git מסמן אותן בקובץ
(`<<<<<<< HEAD` שלך `=======` שלהם `>>>>>>> feature`). עורכים ← `git add` (**מסמן שנפתר**) ← `git commit` (מסיים את המיזוג)
(או `git rebase --continue`). ביטול: `git merge --abort` / `git rebase --abort`.

**אסטרטגיות:** feature branch + **pull request** (סקירת קוד לפני מיזוג) · **Git Flow** (`main` = production,
`develop`, `feature/*`, `release/*`, **`hotfix/*` מתוך `main`**) · **trunk-based** (branches קצרים שממוזגים
כל יום, מוגנים ב-CI).

## 5. תרחיש: באג ב-production בזמן שאתה על ה-branch שלך

אתה על `feature/search` עם **שינויים לא גמורים**; ב-`main` (production) יש באג דחוף.

1. **שמור את העבודה:** `git stash` (או `git commit -m "WIP"`).
2. **עבור ל-production ועדכן:** `git checkout main` ← `git pull`
3. **צור ממנו branch:** `git checkout -b hotfix/login-crash`
4. **תקן, בדוק, commit:** `git add …` ← `git commit -m "Fix login crash"`
5. **Push + PR לתוך main:** `git push -u origin hotfix/login-crash` ← סקירה ← מיזוג ← deploy, tag `v1.2.1`.
6. **חזור לעבודה שלך:** `git checkout feature/search` ← `git stash pop`
7. **קבל גם את התיקון:** `git merge main` (או `git cherry-pick <fix-hash>`).

**למה כך:** התיקון מתחיל **ממה שבאמת ב-production**, לא מהפיצ'ר החצי-גמור שלך; העבודה שלך לא מתערבבת
בתיקון; התיקון עובר סקירה; וה-branch שלך מקבל את התיקון, כדי שהבאג לא יחזור במיזוג.

## 6. התאוששות מאסונות (החלק השני של המעבדה)

| אסון | מה קרה (במודל) | שחזור |
|---|---|---|
| **commits ב-detached HEAD**, ואז עברת ל-branch | ה-commits קיימים, אבל **אף ref** לא מצביע עליהם | `git reflog` ← מצא את ה-hash ← `git checkout -b rescue <hash>` (או `git branch rescue <hash>`) |
| **commits אבודים** אחרי `git reset --hard` | ה-ref של ה-branch זז אחורה; ה-commits בלי ref | `git reflog` ← `git reset --hard <hash>` |
| **rebase שהשתבש** | ה-branch מצביע על commits חדשים ושגויים; הישנים עדיין קיימים | בזמן ה-rebase: `git rebase --abort`; אחריו: `git reflog` ← `git reset --hard <branch>@{n}` (המיקום שלפני ה-rebase; גם `ORIG_HEAD`) |
| **מחקת branch** | רק ה-ref נעלם | `git reflog` ← `git branch <name> <hash>` |

**הלקח:** אובייקטים קבועים ורק refs זזים, ולכן שחזור = למצוא את ה-hash הישן (ב-reflog) ולהצביע עליו
שוב עם ref. עבודה **שלא נשמרה ב-commit** ונמחקה לא ניתנת לשחזור (היא אף פעם לא הייתה אובייקט); ה-reflog
מקומי ופג תוקף אחרי זמן.

## 7. git כדוגמה נגדית לשפה אחידה

**מודל נקי** (אובייקטים, refs, HEAD, שלושת העצים) עם **שפה לא עקבית**:
- `checkout` עושה דברים לא קשורים (ולכן ב-Git 2.23 פיצלו אותו ל-`switch` ו-`restore`);
- ל-`reset` יש 3 משמעויות, והוא גם מוציא קבצים מה-staging;
- **מושג אחד, שלושה שמות:** index = staging area = cache;
- `pull` מסתיר שתי פעולות (fetch + merge).

שמות גרועים ← גם אנשים **וגם סוכנים** משתמשים בכלי לא נכון.

---

## 8. המעבדה של יום שלישי (לפי הסילבוס)

**Porcelain מול plumbing:** porcelain = פקודות למשתמש (branches, commits, tags, staging, remotes); plumbing = פקודות נמוכות על האובייקטים הבסיסיים ועל שלושת האזורים.

**חלק 1: mini git בכ-100 שורות**, מימוש פקודות הבסיס ("**plumbing**") של git:

| פקודה | מה עושה |
|---|---|
| **`hash-object`** | מחשב את ה-hash של קובץ: SHA-1 של `"blob <size>\0" + content`, ועם `-w` שומר אותו (דחוס ב-zlib) ב-`.git/objects/ab/cdef…` (2 התווים הראשונים = שם התיקייה) |
| **`cat-file`** | קורא אובייקט לפי hash: הסוג (`-t`), הגודל (`-s`) או התוכן (`-p`) |
| **`write-tree`** | הופך את ה-**index** לאובייקט tree (ותת-trees) ומדפיס את ה-hash שלו |
| **`commit-tree`** | יוצר commit מ-hash של tree + הורה אופציונלי (`-p`) + הודעה, ומדפיס את ה-hash. הוא **לא** מזיז שום branch (את זה עושים `git update-ref` / `git commit`) |

עוד plumbing מהקבצים של המרצה:
- **`update-index --add --cacheinfo <mode> <hash> <name>`**: הכנסת רשומה ל-index ידנית. Modes: `100644` קובץ רגיל, `100755` קובץ הרצה, `120000` symlink (`040000` = tree ברשימה).
- **`update-ref refs/heads/main <hash>`**: עדכון ref בצורה בטוחה (branch הוא רק קובץ שמכיל hash, למשל `echo <hash> > .git/refs/heads/main`).
- **`symbolic-ref HEAD [refs/heads/test]`**: קריאה או שינוי של HEAD. HEAD הוא **הפניה סמלית (symbolic reference)**: מצביע על **ref אחר**, לא על hash (`ref: refs/heads/main`); `git commit` משתמש ב-commit שהוא מוביל אליו כהורה.
- אובייקט נשמר ב-`.git/objects/` + **2 התווים הראשונים של ה-hash (תיקייה) + 38 הנותרים (שם קובץ)**; ה-hash מחושב על **header + תוכן**. `main^{tree}` = ה-tree של ה-commit האחרון ב-main.
- **אובייקט tag** (סוג אובייקט רביעי, נוצר ב-`git tag -a`): tagger, תאריך, הודעה ומצביע ל-commit; כמו branch ש**לא זז לעולם**.

`git commit` = `write-tree` + `commit-tree` + הזזת ה-ref של ה-branch. פקודות ה"**porcelain**"
(add, commit, checkout) בנויות מעל פקודות אלה.

**חלק 2: התאוששות מכוונת מאסונות:** detached HEAD, commits אבודים, rebase שהשתבש, שחזור דרך
ה-reflog (סעיף 6).

---

## 9. מודלים מנטליים: התיאוריה של Naur ו-DDD

**Naur, *Programming as Theory Building* (1985):** התוצר העיקרי של תכנות הוא **תיאוריה** שהצוות מחזיק: ידע איך חלק מהעולם מטופל על ידי התוכנית, שמאפשר **לעשות, להסביר, להצדיק ולענות על שאלות** (מושג התיאוריה של Ryle).
- **ראיות:** (1) קבוצה B הרחיבה מהדר של קבוצה A עם **קוד מלא, מסמכי תכנון וגישה ל-A**, ובכל זאת התיקונים שלה "הרסו את הכוח והפשטות" של התכנון; A זיהו זאת מיד. (2) כותבי מערכת זמן-אמת של 200,000 שורות מצאו תקלות מהידע שלהם + הקוד; צוותים אחרים עם תיעוד מלא נתקעו שוב ושוב.
- **מסקנה:** אי אפשר לכתוב את התיאוריה במלואה; היא חיה באנשים. תוכנית **חיה** כל עוד צוות שמחזיק את התיאוריה שולט בה, ו**מתה** כשהצוות מתפרק; להחיות אותה רק מהתיעוד "בלתי אפשרי לחלוטין".
- **שלוש יכולות שהתיאוריה נותנת:** (1) **לקשר את התוכנית לעולם** (איזה קוד ↔ איזה חלק בעולם, מה רלוונטי); (2) **להצדיק את התכנון**; (3) **להגיב לשינוי** ב**הרחבה** של התכנון ולא בטלאי. כולן נשענות על זיהוי דמיון, שאי אפשר לכתוב ככללים.
- **הערת המרצה:** AI עם יכולות דמויות "system 1" מחליש את הטענה ש"אי אפשר לבטא", אבל "בעלות" על פרויקט עדיין פירושה שאתה יכול להסביר, להצדיק ולהתאים אותו.

**דוגמת git:** משתמש 1 מכיר את הפקודות (add, commit, checkout -b, merge); משתמש 2 מחזיק את **המודל** (תמונות מצב, אחסון לפי hash, git רק מוסיף, שלושה מצבים, branch הוא מצביע) ויכול **לגזור** התנהגות: branch זול (מצביע אחד), fast-forward = היעד הוא צאצא, commit "אבוד" ניתן לשחזור (שום דבר לא נמחק), conflict = שני ה-branches שינו אותו אזור ביחס לאב משותף. משתמש 1 הוא כמו **קבוצה B**: תיעוד מלא, ונתקע בהפתעה הראשונה.

**תיאוריה מול מפרט (spec):** spec הוא קבוצה סופית של הצהרות מפורשות על **מה** המערכת צריכה לעשות: **תוצר** (תמונת מצב) של התיאוריה. התיאוריה היא **למה** הדרישות האלה ולא אחרות, מה מרכזי ומה שולי, ואיפה התכנון יכול להתמתח. **שני צוותים עם אותו spec ותיאוריות שונות יענו לבקשת השינוי הבאה בדרכים לא תואמות.**

**DDD (Evans, 2003)** נותן *פרקטיקות* לבנות את התיאוריה בכוונה, לשתף אותה ולשמור את הקוד מתואם איתה:
- **מודל תחום** = הפשטה סלקטיבית ומכוונת של מה שהצוות יודע; ההבנה המשותפת, לא דיאגרמה. נבנה ב-**knowledge crunching**: מפתחים + מומחי תחום עוברים על דוגמאות, מוצאים פערים ובונים מחדש.
- Naur ↔ DDD: קישור לעולם ↔ **model-driven design** (מבנה הקוד משקף את המודל); הצדקה ↔ טיעונים **במונחי התחום**; תגובה לשינוי ↔ **refactoring toward deeper insight** (משנים את המודל, לא מוסיפים מקרה מיוחד).
- **השפה האחידה = החלק המשותף והגלוי של התיאוריה.** אוצר מילים אינו תיאוריה, אבל הוא עושה 3 תפקידים: **העברה** (חדשים לומדים כשמתקנים אותם), **זיהוי סחף** (אם שינוי לא מנוסח בטבעיות, הוא יהיה טלאי), **קשירת הקוד לתיאוריה** (שמות בקוד = מונחי התחום). השפה האחידה של git: blob, tree, commit, ref, HEAD, index, working tree.
- **Bounded context = התחום של התיאוריה של צוות אחד**; **context map** מתאר איך התיאוריות של צוותים שונים קשורות.
- **Naur מול DDD:** Naur טוען שאי אפשר לבטא את התיאוריה ושאין שיטה נכונה; DDD אופטימי יותר (להפוך את רובה למפורש) והוא אוסף דפוסים, לא נוהל.
- **עם סוכני AI:** השפה האחידה היא **החלק הזול ביותר של התיאוריה למסור ל-LLM**: מילון מונחים בהוראות, specs שחייבים להשתמש במונחים (למשל יכולות OpenSpec `issue-enrichment`, `issue-routing`), ו**דחיית קוד שמכניס מילים נרדפות או מושגים חדשים**. הצוות נשאר אחראי על הרלוונטיות, על מתי המודל צריך להשתנות ועל שלמות הקוד מול התיאוריה.

## 10. מושגי DDD

**כשקוד זול** (סוכנים כותבים אותו), מודל התחום הוא הנכס שנשאר, וצריך **לכתוב** כמה שיותר ממנו (מילון מונחים, אינווריאנטים, מפרטים).

| מושג | משמעות | דוגמה (מערכת ה-triage שלנו) |
|---|---|---|
| **שפה אחידה (Ubiquitous language)** | **שם מוסכם אחד לכל מושג**, בכל מקום: בשיחה, במפרטים ובקוד. **ממשק שמכונה קוראת**: **שמות משנים באופן מדיד את מה שסוכנים מייצרים** | "severity" = כמה הבאג חמור, אף פעם לא "priority" (ה-`ticket_priority` מתרגיל B בשבוע 1 שבר את זה) |
| **הקשר תחום (Bounded context)** | גבול שבתוכו המונחים של מודל אחד עקביים; אותה מילה יכולה לומר משהו אחר מחוץ לו. נותן **הסתרת מידע** ו**הקשר קטן וממוקד לסוכן** | "component" = תיקיית קוד ב-*routing*, טקסט חופשי ב-*enrichment* |
| **שכבה נגד השחתה (Anti-corruption layer, ACL)** | **שכבת תרגום** שמונעת ממודל חיצוני לחלחל למודל שלך. בפרשנות החדשה: בידוד מפני **מוסכמות שהסוכן מביא מנתוני האימון שלו** | אימות פלט ה-LLM לתוך `TriageRecord` קשיח (דחיית "High", `feature-request`) |
| **ישות (Entity)** | בעלת **זהות** שנשמרת גם כשהנתונים משתנים | issue (repo + מספר) |
| **אובייקט ערך (Value object)** | מוגדר רק על ידי **הערכים** שלו, קבוע | רמת severity |
| **Aggregate / אינווריאנט** | אובייקטים שמשתנים יחד דרך שורש אחד / כלל שתמיד מתקיים | "כל issue אבטחה הולך לתור האבטחה" (שבוע 2) |

**עם סוכנים:** הם מנחשים כל מה שהמודל לא אומר במפורש; מילון מונחים כתוב + גבולות ברורים נותנים להם
את ההקשר הנכון. האובייקטים של git הם מודל תחום טוב (blob הוא **אובייקט ערך**: הזהות = התוכן), אבל שמות
הפקודות שוברים את השפה האחידה.

---

## שאלות ותשובות לתרגול

1. מה המשמעות של "content-addressed" ב-git?<details><summary>Answer</summary>כל אובייקט נשמר ונקרא לפי ה-hash של התוכן שלו: תוכן זהה ← אותו hash, וכל שינוי ← hash חדש. ה-hash הוא גם בדיקת שלמות.</details>
2. מה הם blob, tree ו-commit?<details><summary>Answer</summary>Blob = תוכן של קובץ; tree = רשימת תיקייה (שמות ← hash של blob/tree); commit = tree שורש + הורה/הורים + מחבר, תאריך והודעה.</details>
3. מה זה branch במונחי המודל? למה יצירה שלו זולה?<details><summary>Answer</summary>Ref: מצביע משתנה (קובץ קטן) שמכיל hash של commit ומתקדם בכל commit. יצירה שלו רק כותבת את הקובץ הזה; שום דבר לא מועתק.</details>
4. מה פירוש "refs are mutable pointers into an immutable DAG"?<details><summary>Answer</summary>commits (וכל האובייקטים) לא משתנים ומצביעים על ההורים שלהם, וכך נוצר DAG; רק refs (branches, HEAD) משתנים, כשהם מצביעים על commits אחרים.</details>
5. מה זה HEAD? מה זה detached HEAD, ומה הסיכון?<details><summary>Answer</summary>HEAD = איפה שאתה נמצא, בדרך כלל branch. Detached = מצביע ישירות על commit; commits חדשים שם לא שייכים לאף branch ויכולים "ללכת לאיבוד" כשעוזבים.</details>
6. מה הם שלושת העצים, ומה `add` ו-`commit` עושים להם?<details><summary>Answer</summary>HEAD (ה-commit האחרון), ה-index (ה-commit הבא), תיקיית העבודה (הקבצים בדיסק). add מעתיק מתיקיית העבודה ל-index; commit הופך את ה-index ל-commit חדש ומזיז את ה-branch.</details>
7. מה זה remote?<details><summary>Answer</summary>מאגר אחר (למשל origin ב-GitHub). fetch/push מעתיקים אובייקטים בין מאגרים ומעדכנים refs; origin/main הוא העותק המקומי שלך של ה-branch שלו.</details>
8. git שומר הפרשים או תמונות מצב? למה אי אפשר לשנות היסטוריה בשקט?<details><summary>Answer</summary>תמונות מצב (לכל commit יש tree שורש מלא; קבצים שלא השתנו משתמשים שוב באותו blob). ה-hash של commit כולל את ה-tree וההורים, ולכן שינוי commit ישן משנה את כל ה-hashes שאחריו.</details>
9. הסבר את `git stash` במונחי המודל. `pop` מול `apply`?<details><summary>Answer</summary>שומר שינויים שלא נשמרו כ-commits תחת refs/stash ומחזיר ל-HEAD. pop מחיל מחדש ומוחק את ה-stash; apply מחיל מחדש ומשאיר אותו.</details>
10. מה `git reset` עושה באמת? soft מול mixed מול hard?<details><summary>Answer</summary>מזיז את ה-ref של ה-branch הנוכחי ל-commit אחר. soft: רק ה-ref; mixed (ברירת מחדל): ref + index; hard: ref + index + תיקיית עבודה.</details>
11. מה עושים cherry-pick ו-rebase, ולמה commits אחרי rebase מקבלים hash חדש?<details><summary>Answer</summary>cherry-pick מחיל שינוי של commit אחד כ-commit חדש; rebase עושה cherry-pick לסדרה על בסיס חדש ומזיז את ה-branch. הורים חדשים ← hash חדש, ולכן לא עושים rebase ל-commits שיש כבר לאחרים.</details>
12. reset מול revert?<details><summary>Answer</summary>reset מזיז את ה-branch אחורה וכותב היסטוריה מחדש (רק מקומית). revert מוסיף commit חדש שמבטל שינוי, ולכן בטוח אחרי push.</details>
13. מה זה ה-reflog, ולמה הוא יכול לשחזר commits "אבודים"?<details><summary>Answer</summary>יומן מקומי של כל commit ש-HEAD וכל branch הצביעו עליו. אובייקטים לא נמחקים מיד, אז מוצאים את ה-hash הישן ומצביעים עליו שוב עם ref.</details>
14. עשית commits ב-detached HEAD ואז עברת ל-main. שחזר אותם.<details><summary>Answer</summary>`git reflog` ← מצא את ה-hash של ה-commit האחרון ← `git checkout -b rescue <hash>` (או `git branch rescue <hash>`).</details>
15. rebase השתבש והסתיים. איך מבטלים אותו?<details><summary>Answer</summary>`git reflog` ← מצא את המיקום של ה-branch לפני ה-rebase ← `git reset --hard <hash>` (או ORIG_HEAD). בזמן ה-rebase: `git rebase --abort`.</details>
16. יש באג ב-production בזמן שאתה באמצע פיצ'ר. מה עושים?<details><summary>Answer</summary>`git stash` ← `git checkout main` ← `git pull` ← `git checkout -b hotfix/x` ← תיקון ו-commit ← push + PR לתוך main ← מיזוג, deploy, tag ← `git checkout feature` ← `git stash pop` ← `git merge main`. יוצאים מ-main כי זה מה שב-production, לא העבודה הלא גמורה שלך.</details>
17. מה עושות `hash-object`, `cat-file`, `write-tree` ו-`commit-tree`?<details><summary>Answer</summary>מחשבת hash לקובץ (ושומרת אותו כ-blob); קוראת אובייקט לפי hash; הופכת את ה-index ל-tree; יוצרת commit מ-tree + הורה + הודעה (בלי להזיז branch).</details>
18. למה git הוא דוגמה נגדית לשפה אחידה?<details><summary>Answer</summary>מודל נקי אבל שמות לא עקביים: checkout עושה דברים לא קשורים, ל-reset יש שלוש משמעויות, ו-index = staging area = cache.</details>
19. מה זה מודל תחום, ולמה הוא חשוב יותר כשסוכנים כותבים קוד?<details><summary>Answer</summary>המושגים, הכללים ואוצר המילים המשותפים: התיאוריה של התוכנית שבראש הצוות. הקוד זול, ולכן המודל הוא הנכס שנשאר, והסוכנים מנחשים כל מה שהוא לא אומר.</details>
20. מה זו שפה אחידה? דוגמה?<details><summary>Answer</summary>שם מוסכם אחד לכל מושג, בכל מקום כולל הקוד; השמות משנים באופן מדיד את פלט הסוכן. למשל "severity" אף פעם לא נקרא "priority".</details>
21. מה זה bounded context, ואיך הוא עוזר בניהול ההקשר של AI?<details><summary>Answer</summary>גבול שבתוכו המונחים של מודל אחד עקביים. כמו הסתרת מידע, הוא מאפשר לסוכן לעבוד רק עם המודל של אותו הקשר, וכך ההקשר שלו נשאר קטן.</details>
22. מה זו שכבה נגד השחתה (ACL) בפרשנות לסוכנים?<details><summary>Answer</summary>שכבת תרגום שמונעת ממודל חיצוני להיכנס למודל שלך; לסוכנים: בידוד מפני מוסכמות שהגיעו מנתוני האימון (למשל אימות פלט ה-LLM לתוך TriageRecord קשיח).</details>
23. ישות מול אובייקט ערך? מה זה blob של git?<details><summary>Answer</summary>לישות יש זהות שנשמרת (issue); אובייקט ערך מוגדר על ידי הערכים שלו (severity). blob הוא אובייקט ערך: הזהות שלו היא ה-hash של התוכן.</details>
24. מה 5 הרעיונות במודל המנטלי של git לפי המרצה?<details><summary>Answer</summary>רצף תמונות מצב; פעולות מקומיות (כל ההיסטוריה ב-.git); שלמות באמצעות checksum של SHA-1, תוכן נשמר לפי hash; git רק מוסיף מידע; שלושה מצבים (modified, staged, committed).</details>
25. מה שלושת המצבים של קובץ ושלושת האזורים של פרויקט?<details><summary>Answer</summary>Modified, staged, committed; ה-working tree, ה-staging area (index) וה-git directory (מה ש-clone מעתיק).</details>
26. ערכת קובץ, עשית `git add`, וערכת שוב. מה ייכנס ל-`git commit`?<details><summary>Answer</summary>רק הגרסה שב-staging (הראשונה); השינוי השני נשאר modified ולא staged.</details>
27. מתי מיזוג הוא fast-forward ומתי three-way merge?<details><summary>Answer</summary>Fast-forward כשהיעד הוא צאצא של ה-commit הנוכחי (אין עבודה מתפצלת): המצביע רק זז. אחרת git ממזג את שני הקצוות עם האב המשותף ל-merge commit חדש עם 2 הורים.</details>
28. מה זו הפניה סמלית (symbolic reference)? דוגמה.<details><summary>Answer</summary>ref שמצביע על ref אחר ולא על hash: HEAD מכיל `ref: refs/heads/main`. קוראים/משנים עם `git symbolic-ref`.</details>
29. מה הטענה המרכזית של Naur, ומה הראיות?<details><summary>Answer</summary>תכנות בונה תיאוריה שהצוות מחזיק, ותיעוד לא יכול ללכוד אותה במלואה. קבוצה B, עם קוד ותיעוד מלאים, עדיין הרסה את תכנון המהדר של A; הצוות המקורי של מערכת בת 200 אלף שורות מצא תקלות שאחרים לא מצאו.</details>
30. אילו שלוש יכולות נותנת התיאוריה?<details><summary>Answer</summary>לקשר את התוכנית לעולם, להצדיק את התכנון, ולהגיב לשינוי בהרחבה ולא בטלאי.</details>
31. תיאוריה מול spec?<details><summary>Answer</summary>spec הוא תמונת מצב מפורשת של מה המערכת צריכה לעשות; התיאוריה היא למה, מה מרכזי ואיפה אפשר להתמתח. אותו spec + תיאוריות שונות ← תשובות לא תואמות לשינוי הבא.</details>
32. אילו 3 תפקידים ממלאת השפה האחידה עבור התיאוריה?<details><summary>Answer</summary>העברה (מתקנים חדשים על המונחים), זיהוי סחף (ניסוח מסורבל = טלאי בדרך), וקשירת הקוד לתיאוריה (שמות בקוד = מונחי התחום).</details>
33. איך שני משתמשי git ממחישים את Naur?<details><summary>Answer</summary>אחד מכיר פקודות, השני מחזיק את המודל ויכול לגזור התנהגות (branches זולים, fast-forward, שחזור, conflicts). המשתמש שמכיר רק פקודות הוא כמו קבוצה B: תיעוד מלא, ונתקע בהפתעה הראשונה.</details>
