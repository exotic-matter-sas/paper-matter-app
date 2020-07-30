#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from core.models import FTLOrg, FTLUser, FTLDocument, FTLFolder, FTLDocumentSharing


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
    raw_id_fields = ("org",)


@admin.register(FTLOrg)
class FTLOrgAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = (
        "id",
        "name",
        "slug",
    )


@admin.register(FTLFolder)
class FTLFolderAdmin(MPTTModelAdmin):
    raw_id_fields = (
        "org",
        "parent",
    )


class FTLDocumentSharingInline(admin.TabularInline):
    model = FTLDocumentSharing
    readonly_fields = (
        "pid",
        "created",
        "edited",
    )
    fields = (
        "created",
        "expire_at",
        "password",
        "note",
    )
    extra = 0


@admin.register(FTLDocument)
class FTLDocumentAdmin(admin.ModelAdmin):
    inlines = [
        FTLDocumentSharingInline,
    ]
    search_fields = (
        "pid",
        "title",
        "note",
        "content",
    )
    raw_id_fields = (
        "org",
        "ftl_user",
        "ftl_folder",
    )


@admin.register(FTLDocumentSharing)
class FTLDocumentSharingAdmin(admin.ModelAdmin):
    search_fields = ("pid",)
    raw_id_fields = ("ftl_doc",)
