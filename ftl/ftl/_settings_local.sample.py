"""
Template for setting_local.py file, useful for new contributors

1. Copy file and rename it without the starting underscore => `settings_local.py`
2. Read the to-do comments bellow to set proper value for local settings
"""
from ftl.enums import FTLStorages, FTLPlugins

DEV_MODE = True
DEBUG = True

# Redirect logs to console for easy debugging
LOGGER_LEVEL = 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['console'],
            'level': LOGGER_LEVEL,
        },
        'ftl': {
            'handlers': ['console'],
            'level': LOGGER_LEVEL,
        },
        'setup': {
            'handlers': ['console'],
            'level': LOGGER_LEVEL,
        },
    },
}

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
# BROWSER_BINARY_PATH = '' # to test a specific browser version which is not installed at the default path

# TODO default should be fine unless your dev is related to remote storage and/or OCR
"""
DOCUMENT BINARY STORAGE
=======================
Remote storage requires:
    - extra settings (see EXTRA SETTINGS FOR STORAGE below)
    - extra Python module (see ftl.constants.FTLStorages docstring)
"""
DEFAULT_FILE_STORAGE = FTLStorages.FILE_SYSTEM

# TODO default should be fine unless your dev is related to an OCR
"""
DOCUMENT PROCESSING PLUGINS (order is important)
================================================
- Edit lines below to change enabled plugins
    - Optional plugins required to install additional Python modules
    - Most OCR plugins required a specific DEFAULT_FILE_STORAGE
    - Check ftl.constants.FTLplugins docstring to know what's required for the desired plugin 
- Only one plugin of each type should be enable at a time
"""
FTL_DOC_PROCESSING_PLUGINS = [
    # Extract text of non scanned documents (required)
    FTLPlugins.TEXT_EXTRACTION_TIKA,

    # Detect lang (required for search feature)
    FTLPlugins.LANG_DETECTOR_LANGID,

    # Search feature (required)
    FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR,
]

"""
EXTRA SETTINGS FOR REMOTE STORAGE OR OCR_GOOGLE_VISION_SYNC 
"""
if DEFAULT_FILE_STORAGE == FTLStorages.AWS_S3:
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''
    AWS_S3_ENDPOINT_URL = ''
    AWS_S3_REGION_NAME = ''
    AWS_DEFAULT_ACL = ''
    S3_USE_SIGV4 = True
if DEFAULT_FILE_STORAGE == FTLStorages.GCS or \
   FTLPlugins.OCR_GOOGLE_VISION_SYNC in FTL_DOC_PROCESSING_PLUGINS:
    from google.oauth2 import service_account

    credentials_raw = {}
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(credentials_raw)

    if DEFAULT_FILE_STORAGE == FTLStorages.GCS:
        GS_BUCKET_NAME = ''

# Disable API rate limit during tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'core.models.FTLModelPermissions',
    ),
    'PAGE_SIZE': 10,
}
