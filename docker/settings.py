"""
Django settings for ftl project.

Generated by 'django-admin startproject' using Django 2.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import pathlib
from distutils.util import strtobool

import django_heroku
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', None),
    integrations=[DjangoIntegration()]
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q-2%l!knv+331nqu&ypc+gv&85nd$9*1g1max3692uxfu_!7w8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.getenv("DJANGO_DEBUG", "False")))

ALLOWED_HOSTS = ['*']

# Custom user auth model
AUTH_USER_MODEL = 'core.FTLUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'mptt',
    'rest_framework',
    'webpack_loader',
    'ftl',
    'setup',
    'core',
    'frontend'
]

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

ROOT_URLCONF = 'ftl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'ftl', 'templates'),
                 os.path.join(BASE_DIR, 'core', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ftl.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

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

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/assets/'  # public path
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')  # internal path
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'dist'),  # Webpack final bundle
    os.path.join(BASE_DIR, 'frontend', 'pdfjs'),
    os.path.join(BASE_DIR, 'ftl', 'static'),
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# IPs allowed to see the debug toolbar app
INTERNAL_IPS = ['127.0.0.1']

# Login url used by @login_required decorator
LOGIN_URL = 'login'

# Redirect user to this url after login by default
LOGIN_REDIRECT_URL = '/app'

# Default settings for browser used for functional tests
DEFAULT_TEST_BROWSER = 'firefox'
TEST_BROWSER_HEADLESS = True
DEV_MODE = False

# Django Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 10
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, 'frontend', 'webpack-stats.json'),
    }
}

ATOMIC_REQUESTS = True

# Workaround for configuring a preloaded Tika
os.environ['TIKA_SERVER_JAR'] = pathlib.Path(os.path.join(BASE_DIR, 'vendors', 'tika-server-1.20.jar')).as_uri()

if bool(strtobool(os.getenv("USE_S3", "False"))):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_DEFAULT_ACL = 'private'
    S3_USE_SIGV4 = True

# Configure Django App for Heroku.
django_heroku.settings(locals(), db_colors=False, databases=True, test_runner=False, staticfiles=False,
                       allowed_hosts=False, logging=True, secret_key=True)
