#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import hashlib

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django_otp import devices_for_user
from oauth2_provider.models import get_application_model

from account import signals
from core.models import FTLFolder, FTLDocument, FTLUser, FTLOrg


class Command(BaseCommand):
    help = "Purge and disable/delete account"

    def add_arguments(self, parser):
        parser.add_argument("-o", "--org-slug", nargs="?", type=str, required=True)
        parser.add_argument("-D", "--force-delete", action="store_true", required=False)

    def handle(self, *args, **options):
        delete_account = (
            options["force_delete"] or settings.FTL_DELETE_DISABLED_ACCOUNTS
        )

        org = FTLOrg.objects.get(slug=options["org_slug"])

        self.stdout.write(self.style.MIGRATE_HEADING(f"Purging account {org}..."))

        signals.pre_account_disable.send(sender=self.__class__, org=org)

        # Delete folders inside Root recursively, including their documents
        folders = FTLFolder.objects.filter(org=org, parent=None)
        for folder in folders:
            folder.delete()
            self.stdout.write(f"Deleted {folder}")

        # Also delete documents in root
        documents = FTLDocument.objects.filter(org=org, deleted=False)
        for doc in documents:
            doc.mark_delete()
            self.stdout.write(f"Deleted {doc}")

        self.stdout.write(f"Disable all users in {org}...")
        users = FTLUser.objects.filter(org=org)
        for user in users:
            # Delete otp devices
            two_fa_devices = devices_for_user(user, None)
            for fa_device in two_fa_devices:
                fa_device.delete()

            # Delete oauth2 app and tokens
            get_application_model().objects.filter(user=user).delete()

            # Disable or delete user
            if delete_account:
                user.email = f"{get_random_string(32)}@disabled.pm.app"
            else:
                m = hashlib.md5()
                m.update(user.email.encode("utf-8"))
                user.email = f"{m.hexdigest()}@disabled.pm.app"

            user.first_name = ""
            user.last_name = ""
            user.is_active = False
            user.set_unusable_password()
            user.save()

        org.name = get_random_string(length=32)
        org.slug = slugify(org.name)
        org.deleted = delete_account  # flag for deletion later
        org.save()

        signals.post_account_disable.send(sender=self.__class__, org=org)
