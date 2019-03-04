from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy

"""
Classes based of Django standard auth view for handling of the `org_slug` parameter in URL.
Overloading of get_success_url() to add url parameters to the view.
"""


class PasswordChangeViewFTL(PasswordChangeView):
    def get_success_url(self):
        return reverse_lazy('password_change_done', kwargs=self.kwargs)


class PasswordResetViewFTL(PasswordResetView):
    def get_success_url(self):
        return reverse_lazy('password_reset_done', kwargs=self.kwargs)


class PasswordResetConfirmViewFTL(PasswordResetConfirmView):
    def get_success_url(self):
        return reverse_lazy('password_reset_complete', kwargs=self.kwargs)
