python
======

pip: save all installed packages list

    pip freeze > requirements.txt

pip: update all installed packages

    pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

