from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from core.models import FTLOrg

"""
Classes based of Django standard auth view for handling of the `org_slug` parameter in URL.
Overloading of get_success_url() to add url parameters to the view.
"""


class LoginViewFTL(LoginView):
    def get_context_data(self, **kwargs):
        # Add data to view context
        kwargs['org_name'] = get_object_or_404(FTLOrg, slug=self.kwargs['org_slug']).name
        kwargs['title'] = _('Login')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('app:home', kwargs=self.kwargs)


class PasswordChangeViewFTL(PasswordChangeView):
    def get_context_data(self, **kwargs):
        # Add data to view context
        kwargs['title'] = _('Change password')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('password_change_done', kwargs=self.kwargs)


class PasswordResetViewFTL(PasswordResetView):
    def get_context_data(self, **kwargs):
        # Add data to view context
        kwargs['title'] = _('Reset password')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('password_reset_done', kwargs=self.kwargs)


class PasswordResetConfirmViewFTL(PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        # Add data to view context
        kwargs['title'] = _('Reset password')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('password_reset_complete', kwargs=self.kwargs)
