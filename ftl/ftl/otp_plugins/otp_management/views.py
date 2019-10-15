from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, CreateView
from django_otp.plugins.otp_static.models import StaticDevice


class StaticDeviceList(ListView):
    model = StaticDevice


class StaticDeviceAdd(CreateView):
    model = StaticDevice
    fields = ['name']


class StaticDeviceDelete(DeleteView):
    model = StaticDevice
    success_url = reverse_lazy("otp_staticdevice_list")
