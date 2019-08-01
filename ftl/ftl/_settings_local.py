"""
Template for setting_local.py file, useful for new contributors

1. Copy file and rename it without the starting underscore => `settings_local.py`
2. Read the to-do comments bellow to set proper value for local settings
"""
from ftl.constants import FTLStorages

DEV_MODE = True
DEBUG = True

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

# TODO Doc binary storage, default should be fine unless your dev is related to remote storage and/or OCR
DEFAULT_FILE_STORAGE = FTLStorages.FILE_SYSTEM
# WARNING: Additional settings and Python modules are required if you are not using FTLStorages.FILE_SYSTEM
if DEFAULT_FILE_STORAGE == FTLStorages.AWS_S3:  # Amazon S3 storage
    # Uncomment django-storages + boto3 in requirements.txt
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_STORAGE_BUCKET_NAME = ""
    AWS_S3_ENDPOINT_URL = ""
    AWS_S3_REGION_NAME = ""
    AWS_DEFAULT_ACL = 'private'
    S3_USE_SIGV4 = True
elif DEFAULT_FILE_STORAGE == FTLStorages.GCS:  # Google Cloud Storage
    # Uncomment django-storages + google-cloud-storage in requirements.txt
    from google.oauth2 import service_account

    GS_BUCKET_NAME = ''
    credentials_raw = ''
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(credentials_raw)

# TODO FTL document processing plugins (order is important), default should be fine unless your dev is related to a
# processing plugin
FTL_DOC_PROCESSING_PLUGINS = [
    'core.processing.proc_tika.FTLDocTextExtractionTika',
    # Uncomment ONLY ONE of FTLOCR* plugins below to enable OCR for scanned documents
    # LIMITATION: Most OCR required a specific DEFAULT_FILE_STORAGE, see plugin source for more info
    # WARNING: Additional Python modules are required for some OCR (see below)
    # ------------------------------------------------------------------------
    # 'core.processing.proc_aws_textract.FTLOCRAwsTextract',
    # 'core.processing.proc_google_vision.FTLOCRGoogleVision',  # Uncomment google-cloud-vision in requirements.txt
    # 'core.processing.proc_google_vision_async.FTLOCRGoogleVisionAsync',  # Uncomment google-cloud-vision in require...
    'core.processing.proc_lang.FTLDocLangDetector',
    'core.processing.proc_pgsql_tsvector.FTLDocPgSQLTSVector',
]

