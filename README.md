# ftl-app

Archiving documents solution

## Requirements

 * Python 3.7
 * PostgreSQL 11
 
 ## Install Python modules
 
    python -m pip install requirements.txt
 
 ## i18n
 
 :warning: _Try to avoid raw editing of .po files, use poedit or equivalent instead_
 
 Add a new language or create new key to translate:
 
    python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*
    
 Update values for existing i18n key:
 
    python manage.py makemessages --all
    
 Compile .mo files:
 
    python manage.py compilemessages