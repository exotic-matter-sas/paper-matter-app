#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.core.management import BaseCommand
from django_otp import devices_for_user

from core.models import FTLFolder, FTLDocument, FTLUser, FTLOrg


class Command(BaseCommand):
    help = "Purge and disable account"

    def add_arguments(self, parser):
        parser.add_argument("-o", "--org-slug", nargs="?", type=str, required=True)

    def handle(self, *args, **options):
        org = FTLOrg.objects.get(slug=options["org_slug"])

        self.stdout.write(self.style.MIGRATE_HEADING(f"Purging account {org}..."))

        # Delete folders recursively including documents
        folders = FTLFolder.objects.filter(org=org)
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
            two_fa_devices = devices_for_user(user, None)
            for fa_device in two_fa_devices:
                fa_device.delete()

            user.is_active = False
            user.save()
