from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'orgs', views.FTLOrgViewSet)
router.register(r'ftl-users', views.FTLUserViewSet)
router.register(r'documents', views.FTLDocumentViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
