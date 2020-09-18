#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.


from rest_framework import status
from rest_framework.test import APITestCase

from core.models import FTLUser, FTLOrg
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_folder,
    setup_document,
)
from ftl.settings import CRON_SECRET_KEY


class CronAccountTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        self.user = setup_admin(self.org)

    def test_batch_delete_org(self):
        self.org.deleted = True
        self.org.save()

        client_get = self.client.get(
            f"/crons_account/{CRON_SECRET_KEY}/batch_delete_orgs",
            HTTP_X_APPENGINE_CRON="true",
        )
        self.assertEqual(client_get.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(FTLUser.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(FTLOrg.objects.filter(pk=self.org.pk).exists())

    def test_batch_delete_org_skip(self):
        # Test org is NOT deleted if there are still docs or folders
        folder = setup_folder(self.org, "folder a")
        ftl_document = setup_document(self.org, self.user, folder, "title")
        ftl_document.deleted = True
        ftl_document.save()

        self.org.deleted = True
        self.org.save()

        client_get = self.client.get(
            f"/crons_account/{CRON_SECRET_KEY}/batch_delete_orgs",
            HTTP_X_APPENGINE_CRON="true",
        )
        self.assertEqual(client_get.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(FTLOrg.objects.get(pk=self.org.pk).deleted)
