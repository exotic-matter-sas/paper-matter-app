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
