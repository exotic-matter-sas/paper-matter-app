# ftl-app

Archiving documents solution

## Requirements

 * Python 3.7
 * PostgreSQL 11
 
 ## Install Python modules
 
    python -m pip install requirements.txt
 
 ## i18n
 
 Add a new language or key:
 
    python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*
    
 Update i18n values:
 
    python manage.py makemessages --all
    
 Compile .po and .mo files:
 
    python manage.py compilemessages