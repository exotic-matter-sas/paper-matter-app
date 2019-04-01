from django.urls import path

from . import views
from ftl.custom_view_decorators import setup_state_required

app_name = 'setup'
urlpatterns = [
    path('createorg/', setup_state_required(first_org=False)(views.CreateOrg.as_view()), name='create_first_org'),
    path('createadmin/', setup_state_required(first_org=True, admin=False)(views.CreateAdmin.as_view()),
         name='create_admin'),
    path('success/', views.success, name='success'),
]
