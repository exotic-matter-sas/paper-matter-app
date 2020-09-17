#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.urls import path

from core import views_crons

urlpatterns = [
    path(
        "batch_delete_documents",
        views_crons.BatchDeleteDocument.as_view(),
        name="cron-batch-delete-documents",
    ),
    path(
        "batch_clean_oauth_tokens",
        views_crons.BatchCleanOauthTokens.as_view(),
        name="cron-batch-clean-oauth-tokens",
    ),
]
