#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from unittest.mock import patch

from django.core import management
from django.test import TestCase
from django_otp import devices_for_user

from account.management.commands.disable_account import Command
from account.signals import pre_account_disable
from core.models import FTLDocument, FTLFolder, FTLUser
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_document,
    setup_folder,
    setup_2fa_static_device,
)


class AccountCommandsTests(TestCase):
    def setUp(self):
        self.org = setup_org("To delete A", "to-delete-a")
        self.user_a = setup_admin(self.org, "admin@a.com", "aaa")
        self.folder = setup_folder(self.org, "Folder 1")
        self.doc = setup_document(self.org, self.user_a, self.folder, title="Doc 1")
        self.devices = setup_2fa_static_device(
            self.user_a, codes_list=["AA1222", "BB1222"]
        )

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

        management.call_command("disable_account", org_slug="to-delete-a")

        # org has been disabled
        self.assertTrue(FTLDocument.objects.get(pk=self.doc.pk).deleted)
        self.assertFalse(FTLFolder.objects.filter(pk=self.folder.pk).exists())
        self.assertFalse(FTLUser.objects.get(pk=self.user_a.pk).is_active)
        self.assertFalse(list(devices_for_user(self.user_a, confirmed=None)))

        # org_no_delete was not
        self.assertFalse(FTLDocument.objects.get(pk=doc_no_delete.pk).deleted)
        self.assertTrue(FTLFolder.objects.filter(pk=folder_no_delete.pk).exists())
        self.assertTrue(FTLUser.objects.get(pk=user_no_delete_a.pk).is_active)
        self.assertTrue(list(devices_for_user(user_no_delete_a, confirmed=None)))

    @patch.object(pre_account_disable, "send")
    def test_signal_sent(self, mocked_signal):
        management.call_command("disable_account", org_slug="to-delete-a")
        mocked_signal.assert_called_once_with(sender=Command, org=self.org)
