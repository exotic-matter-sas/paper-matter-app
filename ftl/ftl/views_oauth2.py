#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.utils.decorators import method_decorator
from django_otp.decorators import otp_required
from oauth2_provider import views


@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationView(views.AuthorizationView):
    pass
