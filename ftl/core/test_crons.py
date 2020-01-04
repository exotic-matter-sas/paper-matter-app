#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.


from rest_framework import status
from rest_framework.test import APITestCase

import core
from core.models import FTLDocument
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder


class CronTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(self.org, self.user)
        self.doc_bis = setup_document(self.org, self.user, title=tv.DOCUMENT2_TITLE)

        self.first_level_folder = setup_folder(self.org, name='First level folder')

        self.doc_in_folder = setup_document(self.org, self.user, title='Document in folder',
                                            ftl_folder=self.first_level_folder)

    def test_batch_delete_document(self):
        ftl_document = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document.pid)

        ftl_document.deleted = True
        ftl_document.save()

        client_get = self.client.get('/crons/not-secure/batch-delete-documents')
        self.assertEqual(client_get.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=ftl_document.pid)

        count = FTLDocument.objects.count()
        self.assertTrue(count == 2)
