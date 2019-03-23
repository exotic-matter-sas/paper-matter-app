from django.urls import path

from . import views

app_name = 'setup'
urlpatterns = [
    path('createorg/', views.CreateOrg.as_view(), name='create_org'),
    path('createadmin/', views.CreateAdmin.as_view(), name='create_admin'),
    path('success/', views.success, name='success'),
]
