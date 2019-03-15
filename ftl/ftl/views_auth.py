from django.contrib.auth.views import LoginView

from core.models import FTLUser


class LoginViewFTL(LoginView):
    """
    Custom login view for setting some session variables
    """

    def form_valid(self, form):
        valid = super().form_valid(form)
        org = FTLUser.objects.get(user=self.request.user.id).org
        self.request.session['org_id'] = org.id
        self.request.session['org_name'] = org.name
        return valid
