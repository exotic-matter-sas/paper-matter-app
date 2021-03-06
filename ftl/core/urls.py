#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django.urls import path

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
    path("api/v1/users/me", views.FTLUserView.as_view()),
    path("api/v1/folders", views.FTLFolderList.as_view()),
    path("api/v1/folders/<int:id>", views.FTLFolderDetail.as_view()),
    path("api/v1/documents", views.FTLDocumentList.as_view()),
    path("api/v1/documents/<uuid:pid>", views.FTLDocumentDetail.as_view()),
    path(
        "api/v1/documents/<uuid:dpid>/reminders",
        views.FTLDocumentReminderList.as_view(),
    ),
    path(
        "api/v1/documents/<uuid:dpid>/reminders/<int:rpid>",
        views.FTLDocumentReminderDetail.as_view(),
    ),
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
        "api/v1/documents/<str:pid>/download",
        views.DownloadView.as_view(),
        name="api_download_url",
    ),
    path(
        "api/v1/documents/<str:pid>/download/<str:name>",
        views.ViewDocument.as_view(),
        name="api_document_view",
    ),
    path(
        "api/v1/documents/<str:spid>/temp",
        views.TempDownloadView.as_view(),
        name="api_temp_download_url",
    ),
]
