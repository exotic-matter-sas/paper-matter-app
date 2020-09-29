#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.conf import settings


def ftl_context_data(request):
    if request.user and request.user.is_authenticated:
        return {
            "org_name": request.session["org_name"],
            "axes_enabled": settings.AXES_ENABLED,
        }

    return {}
