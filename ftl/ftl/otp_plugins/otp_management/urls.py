from django.urls import path

from . import views

urlpatterns = [
    path('', views.StaticDeviceList.as_view(), name='otp_staticdevice_list'),
    path('register', views.StaticDeviceAdd.as_view(), name='otp_staticdevice_create'),
    path('<str:pk>', views.StaticDeviceDelete.as_view(), name='otp_staticdevice_delete'),
]
