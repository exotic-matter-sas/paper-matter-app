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
        'PORT': '5432'
    }
}

DEV_MODE = True

EMAIL_SUBJECT_PREFIX = '[TESTS] '
