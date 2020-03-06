#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib import admin

from ftl.otp_plugins.otp_ftl.models import Fido2Device

admin.site.register(Fido2Device)
