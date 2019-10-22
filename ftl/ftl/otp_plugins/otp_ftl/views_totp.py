import qrcode
import qrcode.image.svg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, DeleteView
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice

from ftl.otp_plugins.otp_ftl.forms import TOTPDeviceForm, TOTPDeviceCheckForm


@method_decorator(login_required, name='dispatch')
class TOTPDeviceCheck(LoginView):
    template_name = 'otp_management/totpdevice_check.html'
    form_class = TOTPDeviceCheckForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceAdd(FormView):
    template_name = 'otp_management/totpdevice_form.html'
    form_class = TOTPDeviceForm
    success_url = reverse_lazy('otp_list')

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOPTDeviceViewQRCode(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        device = TOTPDevice.objects.get(pk=pk, user=request.user)
        img = qrcode.make(device.config_url, image_factory=qrcode.image.svg.SvgImage)
        response = HttpResponse(content_type='image/svg+xml')
        img.save(response)

        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceDelete(DeleteView):
    template_name = 'otp_management/totpdevice_confirm_delete.html'
    model = TOTPDevice
    success_url = reverse_lazy('otp_list')
