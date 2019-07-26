import os
from distutils.util import strtobool

import django_heroku
import sentry_sdk
from google.oauth2 import service_account
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', None),
    integrations=[DjangoIntegration()]
)
SECRET_KEY = 'changed-by-django-heroku'
DEBUG = bool(strtobool(os.getenv("DJANGO_DEBUG", "False")))
ALLOWED_HOSTS = ['*']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ftl.ftl_setup_middleware.FTLSetupMiddleware'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'postgres'),
        'PORT': os.getenv('DB_PORT', '5432')
    }
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if bool(strtobool(os.getenv("USE_S3", "False"))):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_DEFAULT_ACL = 'private'
    S3_USE_SIGV4 = True

if bool(strtobool(os.getenv("USE_GCS", "False"))):
    import json

    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = 'GCS_BUCKET_NAME'
    credentials_raw = json.loads(os.environ.get('GCS_CREDENTIALS_CONTENT'))
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(credentials_raw)

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", 'noreply@localhost')

# Configure Django App for Heroku.
django_heroku.settings(locals(), db_colors=False, databases=True, test_runner=False, staticfiles=False,
                       allowed_hosts=False, logging=True, secret_key=True)
