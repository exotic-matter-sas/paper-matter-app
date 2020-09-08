#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from core.models import FTLOrg, FTLUser, FTLDocument, FTLDocumentSharing


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
    list_display = ("org", "email", "is_staff")
    search_fields = ("email__exact",)
    ordering = ("email",)
    raw_id_fields = ("org",)

    def get_search_results(self, request, queryset, search_term):
        # Return empty search result when search is empty instead of returning all objects
        if "q" in request.GET and request.GET["q"].strip():
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            return queryset, use_distinct
        else:
            return queryset.none(), False


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
    )
    extra = 0


@admin.register(FTLDocument)
class FTLDocumentAdmin(admin.ModelAdmin):
    list_display = ("pid",)
    inlines = [
        FTLDocumentSharingInline,
    ]
    search_fields = ("pid__exact",)
    raw_id_fields = (
        "org",
        "ftl_user",
        "ftl_folder",
    )
    readonly_fields = (
        "pid",
        "created",
        "edited",
    )
    fields = (
        "pid",
        "created",
        "edited",
        "size",
        "md5",
        "deleted",
        "ocrized",
        "ocr_retry",
        "type",
    )

    def get_search_results(self, request, queryset, search_term):
        # Return empty search result when search is empty instead of returning all objects
        if "q" in request.GET and request.GET["q"].strip():
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            return queryset, use_distinct
        else:
            return queryset.none(), False


@admin.register(FTLDocumentSharing)
class FTLDocumentSharingAdmin(admin.ModelAdmin):
    search_fields = ("pid__exact",)
    raw_id_fields = ("ftl_doc",)
    readonly_fields = (
        "pid",
        "created",
        "edited",
    )
    fields = (
        "pid",
        "created",
        "edited",
        "password",
    )

    def get_search_results(self, request, queryset, search_term):
        # Return empty search result when search is empty instead of returning all objects
        if "q" in request.GET and request.GET["q"].strip():
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            return queryset, use_distinct
        else:
            return queryset.none(), False


admin.site.unregister(TOTPDevice)
admin.site.unregister(StaticDevice)
