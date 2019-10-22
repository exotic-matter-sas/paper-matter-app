from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, DeleteView
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice

from ftl.otp_plugins.otp_ftl.forms import StaticDeviceForm, StaticDeviceCheckForm


@method_decorator(login_required, name='dispatch')
class StaticDeviceCheck(LoginView):
    template_name = 'otp_management/staticdevice_check.html'
    form_class = StaticDeviceCheckForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class StaticDeviceAdd(FormView):
    template_name = 'otp_management/staticdevice_form.html'
    form_class = StaticDeviceForm
    success_url = reverse_lazy('otp_list')

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class StaticDeviceDelete(DeleteView):
    template_name = 'otp_management/staticdevice_confirm_delete.html'
    model = StaticDevice
    success_url = reverse_lazy("otp_list")
