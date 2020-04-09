#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.core import management
from django.test import TestCase
from django_otp import devices_for_user

from core.models import FTLDocument, FTLFolder, FTLUser
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_document,
    setup_folder,
    setup_2fa_static_device,
)


class AccountCommandsTests(TestCase):
    def test_disable_account(self):
        org_no_delete = setup_org("Not delete A", "not-delete-a")
        user_no_delete_a = setup_admin(org_no_delete, "admin@no-delete.com", "bbb")
        folder_no_delete = setup_folder(org_no_delete, "Folder 1 no delete")
        doc_no_delete = setup_document(
            org_no_delete, user_no_delete_a, folder_no_delete, title="Doc 1 no delete"
        )
        devices_no_delete = setup_2fa_static_device(
            user_no_delete_a, codes_list=["AA1222", "BB1222"]
        )

        org = setup_org("To delete A", "to-delete-a")
        user_a = setup_admin(org, "admin@a.com", "aaa")
        folder = setup_folder(org, "Folder 1")
        doc = setup_document(org, user_a, folder, title="Doc 1")
        devices = setup_2fa_static_device(user_a, codes_list=["AA1222", "BB1222"])

        management.call_command("disable_account", org_slug="to-delete-a")

        # org has been disabled
        self.assertTrue(FTLDocument.objects.get(pk=doc.pk).deleted)
        self.assertFalse(FTLFolder.objects.filter(pk=folder.pk).exists())
        self.assertFalse(FTLUser.objects.get(pk=user_a.pk).is_active)
        self.assertFalse(list(devices_for_user(user_a, confirmed=None)))

        # org_no_delete was not
        self.assertFalse(FTLDocument.objects.get(pk=doc_no_delete.pk).deleted)
        self.assertTrue(FTLFolder.objects.filter(pk=folder_no_delete.pk).exists())
        self.assertTrue(FTLUser.objects.get(pk=user_no_delete_a.pk).is_active)
        self.assertTrue(list(devices_for_user(user_no_delete_a, confirmed=None)))
