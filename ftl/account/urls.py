from django.urls import path

from . import views

urlpatterns = [
    path('', views.AccountView.as_view(), name='account_index'),
    path('email', views.AccountEmailChangeView.as_view(), name='account_email'),
    path('email/<str:token>', views.AccountEmailChangeValidateView.as_view(), name='account_email_validate'),
    path('password', views.AccountPasswordView.as_view(), name='account_password'),
]
