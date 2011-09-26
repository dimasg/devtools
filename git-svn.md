git-svn
=======

Везде git-svn можно заменить на “git svn” если нет такого скрипта или алиаса ...
Клонировать репозиторий целиком:

    git-svn clone -s http://example.com/my_subversion_repo local_dir

Добавить игноры из svn в git

    git-svn show-ignore > .gitignore

Клонировать начиная с какой-то ревизии:

    mkdir local_dir
    git-svn init http://example.com/my_subversion_repo
    git-svn fetch –rREVISION

Обновиться до текущей ревизии:

    git-svn rebase

Закоммитить все закоммиченные в git изменения в svn:

    git-svn dcommit

Внимание! Каждый коммит в git при таком коммите пойдет отдельным коммитом в svn

Branches
--------

Вариант 1: открываем файл .git/config, там будет что-то похожее на:

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

Гит может использовать vim diff для разрешения конфликтов:

    git mergetool -t vimdiff

Прописать его сразу для всех хранилищ:

    git config --global merge.tool vimdiff

Откатить  последнее изменение (коммит),  но не откатывать правки:

    git reset HEAD~1

Откатить (совсем) последнее изменение:

    git reset --hard HEAD~1

Поменять порядок, слить и т.д. последние пять изменений:

    git rebase -i HEAD~5

Посмотреть правки конкретного коммита:

    git show COMMIT_TAG

