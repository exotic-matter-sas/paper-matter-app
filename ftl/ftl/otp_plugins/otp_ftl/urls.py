from django.urls import path

from ftl.otp_plugins.otp_ftl import views, views_static, views_totp, views_fido2

urlpatterns = [
    path('', views.ListOTPDevice.as_view(), name='otp_list'),
    path('check', views.OTPCheckView.as_view(), name="otp_check"),

    path('static/', views_static.StaticDeviceAdd.as_view(), name='otp_static_add'),
    path('static/check', views_static.StaticDeviceCheck.as_view(), name='otp_static_check'),
    path('static/<str:pk>', views_static.StaticDeviceDetail.as_view(), name='otp_static_detail'),
    path('static/<str:pk>/delete', views_static.StaticDeviceDelete.as_view(), name='otp_static_delete'),

    path('totp/', views_totp.TOTPDeviceAdd.as_view(), name='otp_totp_add'),
    path('totp/check', views_totp.TOTPDeviceCheck.as_view(), name='otp_totp_check'),
    path('totp/<str:pk>', views_totp.TOTPDeviceDetail.as_view(), name='otp_totp_detail'),
    path('totp/<str:pk>/delete', views_totp.TOTPDeviceDelete.as_view(), name='otp_totp_delete'),
    path('totp/<str:pk>/qrcode', views_totp.TOPTDeviceViewQRCode.as_view(), name='otp_totp_qrcode'),

    path('fido2/', views_fido2.Fido2DeviceAdd.as_view(), name='otp_fido2_add'),
    path('fido2/check', views_fido2.Fido2Check.as_view(), name='otp_fido2_check'),
    path('fido2/<str:pk>', views_fido2.Fido2DeviceDelete.as_view(), name='otp_fido2_delete'),
    path('fido2/api/register_begin', views_fido2.fido2_api_register_begin, name='otp_fido2_api_register_begin'),
    path('fido2/api/register_finish', views_fido2.fido2_api_register_finish, name='otp_fido2_api_register_finish'),
    path('fido2/api/login_begin', views_fido2.fido2_api_login_begin, name='otp_fido2_api_login_begin'),
]
