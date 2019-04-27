from django.urls import path

from ftl.ftl_setup_middleware import SetupState
from . import views

app_name = 'setup'
urlpatterns = [
    path('createorg/', views.CreateOrg.as_view(), kwargs={"ftl_setup_state": SetupState.none}, name='create_first_org'),
    path('createadmin/', views.CreateAdmin.as_view(), kwargs={"ftl_setup_state": SetupState.first_org_created},
         name='create_admin'),
    path('success/', views.success, name='success'),
]
