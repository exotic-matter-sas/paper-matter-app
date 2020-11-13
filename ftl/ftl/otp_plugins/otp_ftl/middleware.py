#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django_otp import user_has_device
from rest_framework.authentication import SessionAuthentication


class FTLSessionAuthentication(SessionAuthentication):
    """
    Implement authentication 2fa check for internal API calls in the frontend.
    """

    def authenticate(self, request):
        response = super().authenticate(request)

        # response[0] is the user
        if (
            response
            and response[0]
            and (not user_has_device(response[0]) or response[0].is_verified())
        ):
            return response
        else:
            return None
