#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import pytz
from django.conf import settings

from django.utils import timezone, translation


class FTLLocaleMiddleware:
    """
    Set user language and timezone according to the user setting.
    Please note this overwrites Django langage choice in django.middleware.locale.LocaleMiddleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Set timezone from user db
            tzname = request.user.tz or getattr(settings, "TIME_ZONE")
            if tzname:
                timezone.activate(pytz.timezone(tzname))
            else:
                timezone.deactivate()

            # Set language from user db
            lang = request.user.lang or getattr(settings, "LANGUAGE_CODE")
            translation.activate(lang)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang

        return self.get_response(request)
