from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy


class PasswordChangeViewFTL(PasswordChangeView):
    def get_success_url(self):
        return reverse_lazy('password_change_done', kwargs=self.kwargs)


class PasswordResetViewFTL(PasswordResetView):
    def get_success_url(self):
        return reverse_lazy('password_reset_done', kwargs=self.kwargs)


class PasswordResetConfirmViewFTL(PasswordResetConfirmView):
    def get_success_url(self):
        return reverse_lazy('password_reset_complete', kwargs=self.kwargs)
