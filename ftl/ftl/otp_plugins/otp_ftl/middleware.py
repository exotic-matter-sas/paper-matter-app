#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django_otp import user_has_device
from rest_framework.authentication import SessionAuthentication


class FTLSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        response = super().authenticate(request)

        if response and response[0] and (not user_has_device(response[0]) or response[0].is_verified()):
            return response
        else:
            return None
