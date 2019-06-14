# ftl-app

Archiving documents solution

## For users

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Java 8+
 
### Install Python modules
 
    python -m pip install requirements.txt

## For developers

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Firefox or Chrome (to run functional tests)
 * Poedit or equivalent (to add/update i18n)
 * Node.js
 * Java 8+ (for documents indexing)

### Install Python modules
 
    python -m pip install requirements.txt
    python -m pip install requirements_dev.txt

### Install Node modules
 
    cd ftl/vuejs-app
    npm install
    
### Run local server

First terminal

    npm run serve

Second terminal
    
    python manage.py runserver

### Tests

#### Python

Run all tests

    python manage.py test
    
Run test for a specific module

    python manage.py test ftests # run only functional tests
    python manage.py test core # run unit tests of core module

#### VueJS

Run all tests

    vue-cli-service test:unit
    
_Or alternatively `npx vue-cli-service test:unit`_

### i18n
 
 :warning: _Avoid raw editing of .po files, use poedit or equivalent instead_
 
 Add a new language or create new key to translate in .po files:
 
    python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*
    # Following lines needed for frontend i18n
    npm run build
    python manage.py makemessages -l fr --ignore=node_modules -d djangojs

 Update existing i18n key in .po files:
 
    python manage.py makemessages --all
    
 Compile .mo files:
 
    python manage.py compilemessages
    
 _note: generated .mo files aren't versioned and should be regenerated locally after each .po files update._
    
### Django settings

To use specific Django settings without modifying main `ftl/ftl/settings.py` file, create a `ftl/ftl/settings_local.py` file and override desired setting in it.

### Build app

#### 1. compile Vuejs files

    npm run build

#### 2. collect static files to an unique dir using Django

    python3 manage.py collectstatic
    
### Reindex all documents

    python manage.py reindex_docs