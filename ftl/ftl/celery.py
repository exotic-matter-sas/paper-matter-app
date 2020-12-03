#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ftl.settings")
os.environ.setdefault(
    "FORKED_BY_MULTIPROCESSING", "1"
)  # https://github.com/celery/celery/issues/4081

app = Celery("ftl")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
