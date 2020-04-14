#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("uploads/<str:uuid>", views.DownloadView.as_view()),
    path("uploads/<str:uuid>/<str:name>", views.ViewDocument.as_view()),
    path("api/v1/folders", views.FTLFolderList.as_view()),
    path("api/v1/folders/<int:id>", views.FTLFolderDetail.as_view()),
    path("api/v1/documents", views.FTLDocumentList.as_view()),
    path("api/v1/documents/<uuid:pid>", views.FTLDocumentDetail.as_view()),
    path(
        "api/v1/documents/<uuid:pid>/thumbnail.png",
        views.FTLDocumentThumbnail.as_view(),
        name="api_thumbnail_url",
    ),
    path("api/v1/documents/upload", views.FileUploadView.as_view()),
    path("api/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
