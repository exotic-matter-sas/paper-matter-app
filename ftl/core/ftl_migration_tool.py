#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for license information.

from django.contrib.auth.management import create_permissions
from django.core.management.sql import emit_post_migrate_signal

from core.models import FTL_PERMISSIONS_USER


# Group creation + update permissions for FTL Model
def create_group(apps, schema_editor):
    # Workaround for https://code.djangoproject.com/ticket/23422
    # Model permission are only created after the first complete migration so we force create permissions for FTL models
    emit_post_migrate_signal(2, False, "default")

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for app_config in apps.get_app_configs():
        create_permissions(app_config, apps=apps, verbosity=0)

    group, created = Group.objects.get_or_create(name="ftl_users_group")

    for name in FTL_PERMISSIONS_USER:
        app_label, codename = name.split(".", 1)
        permission = Permission.objects.get(
            content_type__app_label=app_label, codename=codename
        )
        group.permissions.add(permission)
        group.save()


def set_all_users_ftl_group(apps, schema_editor):
    FTLUser = apps.get_model("core", "FTLUser")
    Group = apps.get_model("auth", "Group")

    ftl_group = Group.objects.get(name="ftl_users_group")

    all_users = FTLUser.objects.all()
    for user in all_users:
        user.groups.add(ftl_group)
        user.save()


def clean_user_permission(apps, schema_editor):
    FTLUser = apps.get_model("core", "FTLUser")

    all_users = FTLUser.objects.all()
    for user in all_users:
        user.user_permissions.clear()
        user.save()
