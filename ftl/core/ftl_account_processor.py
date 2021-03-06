#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import datetime

import pytz
from django.conf import settings
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice

from core import mimes


def ftl_account_data(request):
    if request.user and request.user.is_authenticated:
        # Calculate the current timezone offset while taking into account any DST offset
        tz = request.user.tz or getattr(settings, "TIME_ZONE", "UTC")
        tz_offset = (
            pytz.timezone(tz).utcoffset(datetime.datetime.utcnow()).total_seconds()
            / 60.0
        )

        return {
            "name": request.user.get_username(),
            "isSuperUser": request.user.is_superuser,
            "otp_warning": any(
                [
                    True
                    for d in devices_for_user(request.user, confirmed=None)
                    if (isinstance(d, StaticDevice) and not d.token_set.exists())
                    or not d.confirmed
                ]
            ),
            "supported_exts": mimes.MIMETYPES_EXT_DICT,
            "only_office_viewer": getattr(settings, "FTL_ENABLE_ONLY_OFFICE", False),
            "tz_offset": tz_offset,
        }

    return {}
