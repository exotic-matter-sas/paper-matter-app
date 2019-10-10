from django.urls import path

from ftl.ftl_setup_middleware import SetupState
from . import views

app_name = 'setup'
urlpatterns = [
    path('createadmin/', views.CreateFirstOrgAndAdmin.as_view(), kwargs={"ftl_setup_state": SetupState.none},
         name='create_admin'),
    path('success/', views.success, name='success'),
]
