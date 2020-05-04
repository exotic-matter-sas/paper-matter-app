#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from unittest.mock import patch

from django.core import management
from django.test import TestCase, override_settings
from django_otp import devices_for_user

from account.management.commands.disable_account import Command
from account.signals import pre_account_disable, post_account_disable
from core.models import FTLDocument, FTLFolder, FTLUser, FTLOrg
from core.tasks import delete_document
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

        self.org_no_delete = setup_org("Not delete A", "not-delete-a")
        self.user_no_delete_a = setup_admin(
            self.org_no_delete, "admin@no-delete.com", "bbb"
        )
        self.folder_no_delete = setup_folder(self.org_no_delete, "Folder 1 no delete")
        self.doc_no_delete = setup_document(
            self.org_no_delete,
            self.user_no_delete_a,
            self.folder_no_delete,
            title="Doc 1 no delete",
        )
        self.devices_no_delete = setup_2fa_static_device(
            self.user_no_delete_a, codes_list=["AA1222", "BB1222"]
        )

    @override_settings(FTL_DELETE_DISABLED_ACCOUNTS=False)
    @patch.object(delete_document, "delay")
    def test_disable_account(self, mocked_delete_document):
        management.call_command("disable_account", org_slug="to-delete-a")

        # org has been disabled
        self.assertTrue(FTLDocument.objects.get(pk=self.doc.pk).deleted)
        self.assertFalse(FTLFolder.objects.filter(pk=self.folder.pk).exists())
        self.assertFalse(FTLUser.objects.get(pk=self.user_a.pk).is_active)
        self.assertFalse(list(devices_for_user(self.user_a, confirmed=None)))
        self.assertFalse(FTLOrg.objects.get(pk=self.org.pk).deleted)

        # org_no_delete was not
        self.assertFalse(FTLDocument.objects.get(pk=self.doc_no_delete.pk).deleted)
        self.assertTrue(FTLFolder.objects.filter(pk=self.folder_no_delete.pk).exists())
        self.assertTrue(FTLUser.objects.get(pk=self.user_no_delete_a.pk).is_active)
        self.assertTrue(list(devices_for_user(self.user_no_delete_a, confirmed=None)))

    @override_settings(FTL_DELETE_DISABLED_ACCOUNTS=True)
    @patch.object(delete_document, "delay")
    def test_delete_account(self, mocked_delete_document):
        management.call_command("disable_account", org_slug="to-delete-a")

        # org has been disabled
        self.assertTrue(FTLDocument.objects.get(org=self.doc.pk).deleted)
        self.assertFalse(FTLFolder.objects.filter(pk=self.folder.pk).exists())
        self.assertFalse(FTLUser.objects.get(pk=self.user_a.pk).is_active)
        self.assertFalse(list(devices_for_user(self.user_a, confirmed=None)))
        self.assertTrue(FTLOrg.objects.get(pk=self.org.pk).deleted)

        # org_no_delete was not
        self.assertFalse(FTLDocument.objects.get(pk=self.doc_no_delete.pk).deleted)
        self.assertTrue(FTLFolder.objects.filter(pk=self.folder_no_delete.pk).exists())
        self.assertTrue(FTLUser.objects.get(pk=self.user_no_delete_a.pk).is_active)
        self.assertTrue(list(devices_for_user(self.user_no_delete_a, confirmed=None)))
        self.assertFalse(FTLOrg.objects.get(pk=self.org_no_delete.pk).deleted)

    @patch.object(delete_document, "delay")
    @patch.object(post_account_disable, "send")
    @patch.object(pre_account_disable, "send")
    def test_signal_sent(
        self, mocked_signal_pre, mocked_signal_post, mocked_delete_document
    ):
        management.call_command("disable_account", org_slug="to-delete-a")
        mocked_signal_pre.assert_called_once_with(sender=Command, org=self.org)
        mocked_signal_post.assert_called_once_with(sender=Command, org=self.org)
