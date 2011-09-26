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


