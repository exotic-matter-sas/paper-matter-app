"""
Template for setting_local.py file, useful for new contributors

1. Copy file and rename it without the starting underscore => `settings_local.py`
2. Read the to-do comments bellow to set proper value for local settings
"""
from ftl.constants import FTLStorages

DEV_MODE = True

# Doc binary storage
DEFAULT_FILE_STORAGE = FTLStorages.FILE_SYSTEM

# TODO create an empty PGSQL DB locally and enter the related data below
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

# TODO configure a local or remote SMTP server (eg. local only postfix, Gmail...)
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_SSL = False

# TODO set preferences to run functional tests
DEFAULT_TEST_BROWSER = 'firefox'  # or 'chrome'
TEST_BROWSER_HEADLESS = True
#  TEST_BROWSER_HEADLESS = False

