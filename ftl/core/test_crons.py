#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.


from rest_framework.test import APITestCase

from core.models import FTLDocument
from core.tasks import batch_delete_doc
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_folder,
    setup_temporary_file,
)


class CronTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(self.org, self.user)
        self.doc_bis = setup_document(self.org, self.user, title=tv.DOCUMENT2_TITLE)

        self.first_level_folder = setup_folder(self.org, name="First level folder")

        self.doc_in_folder = setup_document(
            self.org,
            self.user,
            title="Document in folder",
            ftl_folder=self.first_level_folder,
        )

    def test_batch_delete_document(self):
        binary_f = setup_temporary_file().name
        ftl_document = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document to be deleted",
            binary=binary_f,  # We don't want to delete the test pdf file
        )
        self.assertIsNotNone(ftl_document.pid)
        initial_doc_count = FTLDocument.objects.count()

        ftl_document.deleted = True
        ftl_document.save()

        batch_delete_doc()

        with self.assertRaises(FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=ftl_document.pid)

        self.assertEqual(
            FTLDocument.objects.count(),
            initial_doc_count - 1,
            "Only one doc should have been deleted",
        )
