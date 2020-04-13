# Paper Matter

Archiving documents solution

## For users

### Requirements

 * Python 3.7.3
 * PostgreSQL 11
 * Java 8+
 
### Install Python modules
    cd ftl
    python -m pip install -r requirements.txt

## For developers

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Firefox or Chrome (to run functional tests)
 * Node.js LTS
 * Java 8+ (for documents indexing)
 * Black (Python code formatter)

 * _Under Linux, you may need additional tools to build Python modules which includes C code:_
   * _apt-get install build-essential python3-dev libpq-dev_

### Install Python modules
    cd ftl
    python -m pip install -r requirements.txt
    python -m pip install -r requirements_dev.txt

##### Install additional modules for Windows or Mac OSX
    python -m pip install -r requirements_dev[win|osx].txt

### Install Node modules
 
    cd ftl/frontend
    npm ci
    
### Run local server

First terminal

    cd ftl/frontend
    npm run serve

Second terminal
    
    cd ftl
    python manage.py runserver


_To run local as https (required to test 2fa fido2 devices) use `python manage.py runsslserver` instead. You **must have** `DEBUG` and `DEV_MODE` set to `True` in `settings.py` (set them in your `settings_local.py` wont work, unfortunately) and you may have to use `localhost` domain (in place of the usual ip) in order your browser accept to load the app._

### Code formatting
#### Python
[black](https://black.readthedocs.io/en/stable/index.html) is required for all Python files. There is hard check on the CI
for this and it will fail if the Python code is not properly formatted. Please refer to the official site for setup.
#### Javascript
Default formatter of IntellJ
#### HTML
Default formatter of IntellJ

### Tests

#### Python

_To run functional tests: make sure your `settings.DEFAULT_TEST_BROWSER` is properly set, download the proper webdriver for your version of [Chrome](https://chromedriver.chromium.org/) or [Firefox](https://github.com/mozilla/geckodriver/releases), make sure `chrome`/`firefox` and `chromedriver`/`geckodriver` are registered in your OS path (or alternatively set absolute path for them in settings `BROWSER_BINARY_PATH`, `DEFAULT_CHROMEDRIVER_PATH`/`DEFAULT_GECKODRIVER_PATH`)._

Run all tests

    python manage.py test --parallel
    # Run all tests excepted slow ones (all functional tests are tagged as `slow`)
    python manage.py test --parallel --exclude-tag=slow
    
Run test for a specific module

    python manage.py test ftests # run only functional tests
    python manage.py test core # run unit tests of core module

#### VueJS

Run all tests

    vue-cli-service test:unit
    
_Or alternatively `npx vue-cli-service test:unit`_

### i18n
  
 1 - Add missing keys to translate into .po files (or add a new language):


     python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*


 2 - Update existing translations in .po files:
 
 
     python manage.py makemessages --all
    
 3 - Update/complete translations in .po files
    
 4 -  Compile .mo files:
  
 
    python manage.py compilemessages
 _generated .mo files aren't versioned and should be regenerated locally after each .po files update._
    
### Django settings

To use specific Django settings without modifying main `ftl/ftl/settings.py` file, create a `ftl/ftl/settings_local.py` file and override desired setting in it.

### Build app

#### 1. compile Vuejs files

    npm run build

#### 2. collect static files to an unique dir using Django

    python3 manage.py collectstatic
    
### Reindex all documents

    python manage.py reindex_docs
    
# Credits
 - Programming languages:
   - [Python](https://www.python.org/)
   - [Vue.js](https://vuejs.org/)

 - Main technologies used:
   - Web framework: [Django](https://www.djangoproject.com/)
   - Database: [PostgreSQL](https://www.postgresql.org/)
   - Document storage, [django-storages](https://github.com/jschneier/django-storages) allow to choose between:
     - File system
     - [Google Cloud Storage](https://cloud.google.com/storage/)
     - [Amazon S3](https://aws.amazon.com/s3/)
   - Optical Character Recognition, to choose between:
     - _disable_
     - [Google Cloud Vision API (sync or async)](https://cloud.google.com/vision/docs/)
     - [Amazon Textract API](https://aws.amazon.com/textract/)
   - Document text extraction: [Apache Tika](https://tika.apache.org/)
   - Document preview: [PDF.js](https://mozilla.github.io/pdf.js/)
   - Search engine: [PostgreSQL tsvector](https://www.postgresql.org/docs/10/datatype-textsearch.html)

 - UI:
   - Logo police: [Quicksand](https://github.com/andrew-paglinawan/QuicksandFamily)
   - App Icons: [Font Awesome](https://fontawesome.com/)
   - SVG illustrations: [Undraw](https://undraw.co/)
 