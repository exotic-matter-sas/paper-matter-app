from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListOTPDevice.as_view(), name='otp_list'),
    path('static/', views.StaticDeviceAdd.as_view(), name='otp_static_add'),
    path('static/<str:pk>', views.StaticDeviceDelete.as_view(), name='otp_static_delete'),
    path('totp/', views.TOTPDeviceAdd.as_view(), name='otp_totp_add'),
    path('totp/<str:pk>/qrcode', views.TOPTDeviceViewQRCode.as_view(), name='otp_totp_qrcode'),
    path('totp/<str:pk>', views.TOTPDeviceDelete.as_view(), name='otp_totp_delete'),
    path('fido2/<str:pk>', views.Fido2DeviceDelete.as_view(), name='otp_fido2_delete'),
]
