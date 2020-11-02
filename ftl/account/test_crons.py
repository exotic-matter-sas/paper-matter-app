#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.


from rest_framework.test import APITestCase

from core.models import FTLUser, FTLOrg
from core.tasks import batch_delete_org
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_folder,
    setup_document,
)


class CronAccountTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        self.user = setup_admin(self.org)

    def test_batch_delete_org(self):
        self.org.deleted = True
        self.org.save()

        batch_delete_org()

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

        batch_delete_org()

        self.assertTrue(FTLOrg.objects.get(pk=self.org.pk).deleted)
