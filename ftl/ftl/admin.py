#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django_otp import user_has_device
from django_otp.admin import OTPAdminSite


class FTLAdminSite(OTPAdminSite):
    def __init__(self, name="ftl2faadmin"):
        super().__init__(name)

    def has_permission(self, request):
        if user_has_device(request.user):
            # Call django-otp method
            return super().has_permission(request)
        else:
            # Call original django admin method
            return super(OTPAdminSite, self).has_permission(request)
