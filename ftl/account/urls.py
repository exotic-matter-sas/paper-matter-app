#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.urls import path, include

from . import views, views_oauth2_mgnt

urlpatterns = [
    path("", views.AccountView.as_view(), name="account_index"),
    path("email/", views.AccountEmailChangeView.as_view(), name="account_email"),
    path(
        "email/<str:token>/",
        views.AccountEmailChangeValidateView.as_view(),
        name="account_email_validate",
    ),
    path("activity/", views.AccountActivityView.as_view(), name="account_activity"),
    path("password/", views.AccountPasswordView.as_view(), name="account_password"),
    path(
        "import-export/",
        views.AccountImportExportView.as_view(),
        name="account_import_export",
    ),
    path("delete/", views.AccountDeleteView.as_view(), name="account_delete"),
    path("oauth2/", include("account.urls_oauth2_mgnt", namespace="oauth2_provider")),
]
