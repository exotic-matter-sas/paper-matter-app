#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect


class LoginViewFTL(LoginView):
    """
    Custom login view for setting authentication backend. Needed because we use multiple auth backend (Django axes for
    rate limiting).
    """

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(
            self.request,
            form.get_user(),
            backend="django.contrib.auth.backends.ModelBackend",
        )
        return HttpResponseRedirect(self.get_success_url())
