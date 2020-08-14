#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "ftl.admin.FTLAdminSite"