# dj-justfile
# https://github.com/aclark4life/dj-justfile/blob/main/justfile

default: just-list

# ---------------------------------------- project ----------------------------------------

import 'project.just'

# ---------------------------------------- django ----------------------------------------

# django-admin
[group('django')]
django-admin:
    python manage.py

alias admin := django-admin
alias a := django-admin

# django-dbshell
[group('django')]
django-dbshell:
    python manage.py dbshell

alias dbshell := django-dbshell
alias dbsh := django-dbshell

# django-dumpdata
[group('django')]
django-dumpdata:
    python manage.py dumpdata | python -m json.tool

alias dump := django-dumpdata

# django-su
[group('django')]
django-su: check-venv
    DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput \
        --username=admin --email=`git config user.mail`

alias su := django-su

# django-migrations
[group('django')]
django-migrations: check-venv
    python manage.py makemigrations

alias migrations := django-migrations

# django-migrate
[group('django')]
django-migrate: check-venv
    python manage.py migrate

alias migrate := django-migrate
alias m := django-migrate

# django-serve
[group('django')]
django-serve: check-venv
    npm run watch &
    python manage.py runserver

alias s := django-serve

# django-shell
[group('django')]
django-shell: check-venv
    python manage.py shell
alias shell := django-shell
alias sh := django-shell

# django-startapp
[group('django')]
django-startapp app_label:
    python manage.py startapp {{ app_label }}
alias startapp := django-startapp

# django-sqlmigrate
[group('django')]
django-sqlmigrate app_label migration_name:
    python manage.py sqlmigrate {{ app_label }} {{ migration_name }}

alias sqlmigrate := django-sqlmigrate

# django-project
[group('django')]
django-project project_name:
    django-admin startproject {{ project_name }}

# django-urls
[group('django')]
django-urls: check-venv
    python manage.py show_urls

alias urls := django-urls

# django-install
[group('django-utils')]
django-install: check-venv pip-install

# open django
[group('django-utils')]
django-open:
    open http://0.0.0.0:8000

alias o := django-open

# ---------------------------------------- git ----------------------------------------

# git commit with last commit message
[group('git')]
git-commit-last:
    git log -1 --pretty=%B | git commit -a -F -
    git push

alias last := git-commit-last

# git commit and push
[group('git')]
git-commit-push:
    git commit -a -m "Add/update dj-justfile recipes."
    git push

alias cp := git-commit-push

# git commit, edit commit message, and push
[group('git')]
git-commit-edit-push:
    git commit -a
    git push

alias ce := git-commit-edit-push

# git log
[group('git')]
git-log:
    git log --oneline

alias log := git-log

# ---------------------------------------- just ----------------------------------------

# list all available recipes
[group('just')]
just-list:
    @just -l

alias l := just-list

# edit the justfile
[group('just')]
just-edit:
    @just -e

alias e := just-edit

# ---------------------------------------- npm ----------------------------------------

# npm run build
[group('npm')]
npm-build:
    npm run build

# npm install
[group('npm')]
npm-install:
    npm install

# npm-install and npm-build
[group('npm')]
npm-init: npm-install npm-build

alias n := npm-init
alias pack := npm-init

# ---------------------------------------- python ----------------------------------------

# save requirements to requirements.txt
[group('python')]
pip-freeze:
    pip freeze > requirements.txt

alias freeze := pip-freeze

# install requirements from requirements.txt
[group('python')]
pip-install:
    pip install -U pip
    export PIP_SRC=src && pip install -r requirements.txt

alias install := pip-install
alias i := pip-install

# ensure virtual environment is active
[group('python')]
check-venv:
    #!/bin/bash
    PYTHON_PATH=$(which python)
    if [[ $PYTHON_PATH == *".venv/bin/python" ]]; then
      echo "Virtual environment is active."
    else
      echo "Virtual environment is not active."
      exit 1
    fi
