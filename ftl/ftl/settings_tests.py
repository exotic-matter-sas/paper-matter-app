try:
    from .settings import *
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'reset',
        'USER': 'postgres',
        'PASSWORD': 'bleubleu',
        'HOST': 'postgres',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True
    }
}

DEFAULT_TEST_BROWSER = 'chrome'

DEV_MODE = True

EMAIL_SUBJECT_PREFIX = '[TESTS] '

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
