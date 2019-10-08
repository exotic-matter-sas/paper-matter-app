from django.urls import path

from . import views

urlpatterns = [
    path('', views.Fido2DeviceList.as_view(), name='otp_webauthn_list'),
    path('register', views.Fido2Register.as_view(), name='otp_webauthn_register'),
    path('<str:pk>', views.Fido2DeviceDelete.as_view(), name='otp_webauthn_delete'),
    path('api/register_begin', views.fido2_api_register_begin, name='otp_webauthn_api_register_begin'),
    path('api/register_finish', views.fido2_api_register_finish, name='otp_webauthn_api_register_finish'),
    path('api/login_begin', views.fido2_api_login_begin, name='otp_webauthn_api_login_begin'),
]
