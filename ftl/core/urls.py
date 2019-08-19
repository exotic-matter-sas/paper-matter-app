from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('uploads/<str:uuid>', views.DownloadView.as_view()),
    path('api/v1/folders', views.FTLFolderList.as_view()),
    path('api/v1/folders/<int:id>', views.FTLFolderDetail.as_view()),
    path('api/v1/documents', views.FTLDocumentList.as_view()),
    path('api/v1/documents/<uuid:pid>', views.FTLDocumentDetail.as_view()),
    path('api/v1/documents/<uuid:pid>/thumbnail.png', views.FTLDocumentThumbnail.as_view()),
    path('api/v1/documents/upload', views.FileUploadView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),
]
