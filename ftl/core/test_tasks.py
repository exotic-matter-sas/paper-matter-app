#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.


from rest_framework.test import APITestCase

from core.models import FTLDocument, FTLOrg
from core.tasks import batch_delete_doc, batch_delete_org
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_folder,
    setup_temporary_file,
)


class RecurringTasksTests(APITestCase):
    def setUp(self):
        self.org_with_docs = setup_org()
        setup_admin(self.org_with_docs)
        self.user = setup_user(self.org_with_docs)

        self.doc = setup_document(self.org_with_docs, self.user)
        self.doc_bis = setup_document(self.org_with_docs, self.user, title=tv.DOCUMENT2_TITLE)

        self.first_level_folder = setup_folder(self.org_with_docs, name="First level folder")

        self.doc_in_folder = setup_document(
            self.org_with_docs,
            self.user,
            title="Document in folder",
            ftl_folder=self.first_level_folder,
        )

        self.org_with_folders = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        setup_folder(self.org_with_folders)

        self.org_without_docs_1 = setup_org(name=tv.ORG_NAME_3, slug=tv.ORG_SLUG_3)
        self.org_without_docs_2 = setup_org(name=tv.ORG_NAME_4, slug=tv.ORG_SLUG_4)

    def test_batch_delete_document(self):
        binary_f = setup_temporary_file().name
        ftl_document = FTLDocument.objects.create(
            org=self.org_with_docs,
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

    def test_batch_delete_org(self):
        # given
        # org_with_docs marked as deleted
        # org_with_folders marked as deleted
        # org_without_docs_1 not marked as deleted
        # org_without_docs_2 marked as deleted
        self.org_with_docs.deleted = True
        self.org_with_docs.save()
        self.org_with_folders.deleted = True
        self.org_with_folders.save()
        self.org_without_docs_2.deleted = True
        self.org_without_docs_2.save()

        # when
        batch_delete_org()

        # then, only orgs marked as deleted AND with no docs or folders left are deleted
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_with_docs.pk).exists())
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_with_folders.pk).exists())
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_without_docs_1.pk).exists())
        self.assertFalse(FTLOrg.objects.filter(pk=self.org_without_docs_2.pk).exists())
