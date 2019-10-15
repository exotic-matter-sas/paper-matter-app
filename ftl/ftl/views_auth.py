from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django_otp.forms import OTPTokenForm


class OTPCheckView(LoginView):
    template_name = 'ftl/registration/otp_check.html'
    form_class = OTPTokenForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
