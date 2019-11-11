from django.urls import path

from . import views

urlpatterns = [
    path('', views.AccountView.as_view(), name='account_index'),
    path('email', views.AccountEmailView.as_view(), name='account_email'),
    path('password', views.AccountPasswordView.as_view(), name='account_password'),
]
