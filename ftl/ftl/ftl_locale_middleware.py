#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for license information.

import pytz

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
            tzname = request.user.tz
            if tzname:
                timezone.activate(pytz.timezone(tzname))

            # Set language from user db
            lang = request.user.lang
            if lang:
                translation.activate(lang)
                request.session[translation.LANGUAGE_SESSION_KEY] = lang
                request.LANGUAGE_CODE = lang

        return self.get_response(request)
