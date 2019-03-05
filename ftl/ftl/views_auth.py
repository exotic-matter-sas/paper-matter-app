from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from core.models import FTLOrg

"""
Classes based of Django standard auth view for handling of the `org_slug` parameter in URL.
Overloading of get_success_url() to add url parameters to the view.
"""


class LoginViewFTL(LoginView):

    def get_context_data(self, **kwargs):
        # Add org_name to view context
        kwargs['org_name'] = get_object_or_404(FTLOrg, slug=self.kwargs['org_slug']).name
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('app:home', kwargs=self.kwargs)


class PasswordChangeViewFTL(PasswordChangeView):
    def get_success_url(self):
        return reverse_lazy('password_change_done', kwargs=self.kwargs)


class PasswordResetViewFTL(PasswordResetView):
    def get_success_url(self):
        return reverse_lazy('password_reset_done', kwargs=self.kwargs)


class PasswordResetConfirmViewFTL(PasswordResetConfirmView):
    def get_success_url(self):
        return reverse_lazy('password_reset_complete', kwargs=self.kwargs)
