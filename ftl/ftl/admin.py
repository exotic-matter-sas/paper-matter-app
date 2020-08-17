#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.urls import reverse
from django_otp import user_has_device
from django_otp.admin import OTPAdminSite


class FTLAdminSite(OTPAdminSite):
    login_form = None
    login_template = None

    def __init__(self, name="ftl2faadmin"):
        super().__init__(name)

    def has_permission(self, request):
        if user_has_device(request.user):
            # Call django-otp method
            return super().has_permission(request)
        else:
            # Call original django admin method
            return super(OTPAdminSite, self).has_permission(request)

    def login(self, request, extra_context=None):
        # redirect to ftl login instead of using the admin login page (for 2fa support)
        resp = super().login(request, extra_context)

        if not request.user.is_authenticated:
            resp = redirect_to_login(reverse("admin:index", current_app=self.name))
        elif not request.user.is_staff:
            return HttpResponseForbidden()

        return resp
