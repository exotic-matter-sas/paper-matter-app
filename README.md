# ftl-app

Archiving documents solution

## For users

### Requirements

 * Python 3.7
 * PostgreSQL 11
 
### Install Python modules
 
    python -m pip install requirements.txt
        
## For developers

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Firefox or Chrome (to run functional tests)
 * Poedit or equivalent (to add/update i18n)
 
### Install Python modules
 
    python -m pip install requirements_dev.txt
 
### Tests

Run all tests

    python manage.py test
    
Run test for a specific module

    python manage.py test ftests # run only functional tests
    python manage.py test core # run unit tests of core module
 
### i18n
 
 :warning: _Avoid raw editing of .po files, use poedit or equivalent instead_
 
 Add a new language or create new key to translate:
 
    python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*
    
 Update values for existing i18n key:
 
    python manage.py makemessages --all
    
 Compile .mo files:
 
    python manage.py compilemessages
    
### Django settings

To use specific Django settings without modifying main `ftl/ftl/settings.py` file, create a `ftl/ftl/settings_local.py` file and override desired setting in it.