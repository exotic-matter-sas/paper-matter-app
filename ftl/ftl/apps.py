#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "ftl.admin.FTLAdminSite"
