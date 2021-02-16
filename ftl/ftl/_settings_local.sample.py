#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
"""
Template for setting_local.py file, useful for new contributors

1. Copy file and rename it without the starting underscore => `settings_local.py`
2. Read the to-do comments bellow to set proper value for local settings
"""
import sys

from ftl.enums import FTLStorages, FTLPlugins

DEV_MODE = True
DEBUG = True

# Redirect logs to console for easy debugging
LOGGER_LEVEL = "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler",},},
    "loggers": {
        "core": {"handlers": ["console"], "level": LOGGER_LEVEL,},
        "ftl": {"handlers": ["console"], "level": LOGGER_LEVEL,},
        "setup": {"handlers": ["console"], "level": LOGGER_LEVEL,},
    },
}

# TODO create an empty PGSQL DB locally and enter the related data below
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

# TODO configure a local or remote SMTP server (eg. local only postfix, Gmail...)
EMAIL_HOST = "localhost"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 25
EMAIL_USE_SSL = False

# TODO set preferences for functional tests
DEFAULT_TEST_BROWSER = "chrome"
TEST_BROWSER_HEADLESS = True

# Update lines below if you don't want to use the default paths for browser and driver
BROWSER_BINARY_PATH = None
DEFAULT_CHROMEDRIVER_PATH = "chromedriver"
DEFAULT_GECKODRIVER_PATH = "geckodriver"

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
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_STORAGE_BUCKET_NAME = ""
    AWS_S3_ENDPOINT_URL = ""
    AWS_S3_REGION_NAME = ""
    AWS_DEFAULT_ACL = ""
    S3_USE_SIGV4 = True
if (
    DEFAULT_FILE_STORAGE == FTLStorages.GCS
    or FTLPlugins.OCR_GOOGLE_VISION_SYNC in FTL_DOC_PROCESSING_PLUGINS
):
    from google.oauth2 import service_account

    credentials_raw = {}
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
        credentials_raw
    )

    if DEFAULT_FILE_STORAGE == FTLStorages.GCS:
        GS_BUCKET_NAME = ""

# Monkey patch REST_FRAMEWORK settings to disable rate limit during dev
from .settings import REST_FRAMEWORK

del REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]
del REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]

"""
URI of the instance
This is the host address which will be used to generate an absolute URI if there is none given by the current http
request. It must include the scheme and port.
"""
FTL_EXTERNAL_HOST = "http://127.0.0.1:8000"

# TODO to tests Only Office integration follow instructions below
"""
OnlyOffice integration
To test:
1. Fill Only Office instance settings
2. Set FTL_ENABLE_ONLY_OFFICE to True
3. Build frontend
4. Run PM without `run serve`
5. Open PM through FTL_EXTERNAL_HOST url
"""
FTL_ENABLE_ONLY_OFFICE = False
FTL_ONLY_OFFICE_PUBLIC_JS_URL = ""
FTL_ONLY_OFFICE_API_SERVER_URL = ""
FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL = ""
FTL_ONLY_OFFICE_SECRET_KEY = ""

ALLOWED_HOSTS = ["*"]

# TODO to test code related to API access token expiration easily, uncomment the lines below
# from .settings import OAUTH2_PROVIDER
# OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"] = 10

# Switch CSP to report only to not block contents when using `run dev` (front unbuilt)
CSP_REPORT_ONLY = True
# TODO if you have enabled FTL_ENABLE_ONLY_OFFICE
#  You should uncomment lines below and add FTL_ONLY_OFFICE_API_SERVER_URL to CSP_SCRIPT_SRC and CSP_FRAME_SRC tuples
# from .settings import CSP_SCRIPT_SRC, CSP_FRAME_SRC
# CSP_SCRIPT_SRC += ("",)
# CSP_FRAME_SRC += ("",)

# Required for static files to be properly loaded when running ftests with `run dev` in local
TESTING = sys.argv[1:2] == ["test"]
if TESTING:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
