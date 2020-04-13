#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from core.models import FTLOrg, FTLUser, FTLDocument, FTLFolder

admin.site.register(FTLOrg)
admin.site.register(FTLDocument)
admin.site.register(FTLFolder, MPTTModelAdmin)


@admin.register(FTLUser)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("org", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("org", "email", "password1", "password2",),
            },
        ),
    )
    list_display = ("org", "email", "first_name", "last_name", "is_staff")
    search_fields = ("org__name", "email", "first_name", "last_name")
    ordering = ("email",)
