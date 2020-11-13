#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice

from core import mimes


def ftl_account_data(request):
    if request.user and request.user.is_authenticated:
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
        }

    return {}
