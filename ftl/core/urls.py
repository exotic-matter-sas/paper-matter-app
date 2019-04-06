from django.urls import path, include

from . import views

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'orgs', views.FTLOrgViewSet)
# router.register(r'ftl-users', views.FTLUserViewSet)
# router.register(r'documents', views.FTLDocumentViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    # path('api/v1/', include(router.urls)),
    path('uploads/<str:uuid>', views.DownloadView.as_view()),
    path('api/v1/documents/', views.FTLDocumentList.as_view()),
    path('api/v1/documents/<uuid:pid>', views.FTLDocumentDetail.as_view()),
    path('api/v1/documents/upload', views.FileUploadView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
