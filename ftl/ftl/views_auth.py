from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django_otp.forms import OTPTokenForm


class LoginViewFTL(LoginView):
    """
    Custom login view for setting some session variables
    (not used anymore, replaced by signals)
    """

    def form_valid(self, form):
        valid = super().form_valid(form)
        org = self.request.user.org
        self.request.session['org_id'] = org.id
        self.request.session['org_name'] = org.name
        return valid


class OTPCheckView(LoginViewFTL):
    template_name = 'ftl/registration/otp_check.html'
    form_class = OTPTokenForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
