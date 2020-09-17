#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.urls import path

from account import views_crons

urlpatterns = [
    path(
        "batch_delete_orgs",
        views_crons.BatchDeleteOrg.as_view(),
        name="cron-batch-delete-org",
    ),
]
