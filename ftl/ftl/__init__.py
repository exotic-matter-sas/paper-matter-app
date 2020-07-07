#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import ftl.signals.handlers
from .celery import app as celery_app

__all__ = ("celery_app",)
