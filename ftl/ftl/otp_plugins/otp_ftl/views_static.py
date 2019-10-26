from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import FormView, DeleteView, DetailView
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice

from ftl.otp_plugins.otp_ftl.forms import StaticDeviceForm, StaticDeviceCheckForm


@method_decorator(login_required, name='dispatch')
class StaticDeviceCheck(LoginView):
    template_name = 'otp_ftl/staticdevice_check.html'
    form_class = StaticDeviceCheckForm
    success_url = reverse_lazy('home')

    def get_success_url(self):
        url = self.request.session.get('next', None)
        if url:
            del self.request.session['next']
            url_is_safe = is_safe_url(
                url=url,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            return url if url_is_safe else self.success_url

        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class StaticDeviceDetail(DetailView):
    template_name = 'otp_ftl/staticdevice_detail.html'
    model = StaticDevice


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class StaticDeviceAdd(FormView):
    template_name = 'otp_ftl/staticdevice_form.html'
    form_class = StaticDeviceForm

    def get_success_url(self):
        return reverse_lazy('otp_static_detail', kwargs={'pk': self.instance.id})

    def form_valid(self, form):
        self.instance = form.save(self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class StaticDeviceDelete(DeleteView):
    template_name = 'otp_ftl/staticdevice_confirm_delete.html'
    model = StaticDevice
    success_url = reverse_lazy("otp_list")
