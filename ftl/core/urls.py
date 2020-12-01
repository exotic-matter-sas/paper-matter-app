#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views, views_share_doc

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "share/<uuid:pid>",
        views_share_doc.ViewSharedDocument.as_view(),
        name="view_sharing_doc",
    ),
    path(
        "share/<uuid:pid>/download",
        views_share_doc.DownloadSharedDocument.as_view(),
        name="view_sharing_doc_download",
    ),
    path("api/v1/accounts/me", views.FTLAccountView.as_view()),
    path("api/v1/folders", views.FTLFolderList.as_view()),
    path("api/v1/folders/<int:id>", views.FTLFolderDetail.as_view()),
    path("api/v1/documents", views.FTLDocumentList.as_view()),
    path("api/v1/documents/<uuid:pid>", views.FTLDocumentDetail.as_view()),
    path("api/v1/documents/<uuid:pid>/share", views.FTLDocumentSharingList.as_view()),
    path(
        "api/v1/documents/<uuid:pid>/share/<uuid:spid>",
        views.FTLDocumentSharingDetail.as_view(),
    ),
    path(
        "api/v1/documents/<uuid:pid>/thumbnail.png",
        views.FTLDocumentThumbnail.as_view(),
        name="api_thumbnail_url",
    ),
    path("api/v1/documents/upload", views.FileUploadView.as_view()),
    path(
        "api/v1/documents/<str:uuid>/download",
        views.DownloadView.as_view(),
        name="api_download_url",
    ),
    path(
        "api/v1/documents/<str:uuid>/download/<str:name>",
        views.ViewDocument.as_view(),
        name="api_document_view",
    ),
    path("api/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
