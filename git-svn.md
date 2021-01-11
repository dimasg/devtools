git-svn
=======

Везде git-svn можно заменить на **“git svn”** если нет такого скрипта или алиаса ...

Клонировать репозиторий целиком:

    git-svn clone -s http://example.com/my_subversion_repo local_dir

Добавить игноры из **svn** в **git**

    git-svn show-ignore > .gitignore

Клонировать начиная с какой-то ревизии:

    mkdir local_dir
    git-svn init http://example.com/my_subversion_repo
    git-svn fetch -rREVISION

Обновиться до текущей ревизии:

    git-svn rebase

Закоммитить все закоммиченные в **git** изменения в **svn**:

    git-svn dcommit

Внимание! Каждый коммит в **git** при таком коммите пойдет отдельным коммитом в **svn**

Проблема1: если есть локальные изменения, **git** не даст сделать `svn rebase`

Решение: «прячем» правки с помощью `git-stash`, делаем `rebase`, возвращаем правки через `git-stash apply (git-stash pop)`

Проблема2: **ccollab** не понимает **git** напрямую или его **diff**ы

Решение: `ccollab  addfiles new <files>` для файла без изменений (используем `git-stash` если они уже есть), потом `ccollab addchanges <review #> <files>`

Решение2: [cc-review.py](https://raw.github.com/dimasg/devtools/master/cc-review.py), готовый скрипт для создания ревью из закомиченных изменений текущей ветки

Решение3: `git diff --patch --no-prefix` (требует проверки)

Проблема3: Как сделать так, чтобы правки ушли в **svn** одним коммитом?

Решение: делаем для правок новую ветку `git checkout -b new_branch_name`
Когда всё сделано, мержим её через `git merge --squash <feature_branch> -m <msg>`.
`--squash` собственно и «сжимает» все коммиты в один, после чего остается сделать `dcommit`. Если забыли указать корректное сообщение для мержа, добавить еще один файл и т.д., можно это сделать перед коммитом в **svn** с помощью `git commit --amend`.

Проблема4: svn::externals

Решение: есть удобный скрипт (точнее набор скриптов) [git-svn-clone-externals](https://github.com/andrep/git-svn-clone-externals) который облегчает линковку на дополнительные svn репозитории и обновление из них.

Branches
--------

Открываем файл **.git/config**, там будет что-то похожее на:

    [svn-remote "svn"]
        url = svn+ssh://your-server/home/svn/project-name/trunk
        fetch = :refs/remotes/git-svn

Добавляем нужный бранч:

    [svn-remote "svn34"]
        url = svn+ssh://your-server/home/svn/project-name/branches/3.4.x
        fetch = :refs/remotes/git-svn-3.4

Вытаскиваем нужный бранч:

    git-svn fetch svn34 -r MMMM

Дальше остается только перейти на этот бранч, создать на нём нужный рабочий бранч, дальше как всегда:

    git checkout git-svn-3.4
    git checkout -b master-3.4.x


Tools
-----

Гит может использовать **vimdiff** для разрешения конфликтов:

    git mergetool -t vimdiff

Прописать его сразу для всех хранилищ:

    git config --global merge.tool vimdiff

Откатить  последнее изменение (коммит),  но не откатывать правки:

    git reset HEAD~1

Откатить (совсем) последнее изменение:

    git reset --hard HEAD~1

Просмотреть историю всех сделанных изменений:

    git reflog    <- каждое изменение будет помечено HEAD@{index}, можно откатиться до него git reset HEAD@{index}

Поменять порядок, слить и т.д. последние пять изменений:

    git rebase -i HEAD~5

Посмотреть правки конкретного коммита:

    git show COMMIT_TAG

Посмотреть файлы, измененные в конкретном коммите:

    git show --pretty="format:" --name-only COMMIT_TAG

Посмотреть содержимое последнего stash`а в виде патча:

    git stash show -p stash{0}

Переименовать stash:

    git stash drop stash@{N}    <- тут надо запомнить SHA, который вернет команда
    git stash store -m "Next stash name" XXXX <- XXX - SHA, который вернула предыдущая команда

Поискать в коммитах (особенно удобно искать удаленные строки):

    git log -S<text> <filename>|<-- path_containing_change> [--since=YYYY.MM.DD] [--until=YYYY.MM.DD]

Показать правки по одному файлу из stash`а с номером N:

    git diff stash@{N}^1 stash@{N} -- <filename>

Сразу применить эти правки:

    git diff stash@{N}^1 stash@{N} -- <filename> | git apply

Перенести git svn на новый url:

    изменить svn-remote в .git/config
    git svn fetch [<svn=remote name>] (должен загрузить хотя бы одно новое изменение! указываем svn-remote имя для бранча!)
    возвращаем прежний svn-remote в .git/config
    git svn rebase -l
    опять меняем svn-remote на новый url
    все, теперь git svn rebase должен работать с новым адресом

