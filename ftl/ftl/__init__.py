#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import ftl.signals.handlers
from .celery import app as celery_app

__all__ = ("celery_app",)
