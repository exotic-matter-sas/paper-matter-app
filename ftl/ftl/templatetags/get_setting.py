#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django import template
from django.conf import settings

register = template.Library()

ALLOW_SETTINGS = ("FTL_ENABLE_DEV_API",)


@register.simple_tag
def get_setting(name):
    if name in ALLOW_SETTINGS:
        return getattr(settings, name, None)
    return None
