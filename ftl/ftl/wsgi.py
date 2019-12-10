"""
WSGI config for ftl project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ftl.settings')

application = get_wsgi_application()
