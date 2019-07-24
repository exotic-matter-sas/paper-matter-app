import os
import tempfile

from django.core.exceptions import ValidationError
from django.test import TestCase

import core
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_folder, setup_document, \
    setup_temporary_file
from ftl.settings import BASE_DIR
from .models import FTLUser, FTLDocument, FTLFolder


class FTLUserModelTest(TestCase):
    def test_ftl_user_must_have_an_org(self):
        """FTLUser must have and org set"""
        with self.assertRaises(ValidationError):
            try:
                FTLUser(username=tv.USER1_USERNAME,
                        password=tv.USER1_PASS).full_clean()
            except ValidationError as e:
                self.assertIn('org', str(e))
                raise

    def test_ftl_documents_must_have_user_and_org(self):
        """FTLDocument must have an user and org set"""
        with self.assertRaises(ValidationError):
            try:
                FTLDocument(title=tv.USER1_USERNAME).full_clean()
            except ValidationError as e:
                self.assertIn('user', str(e))
                self.assertIn('org', str(e))
                raise

    def test_ftl_folder_must_have_an_org(self):
        """FTLFolder must have org set"""
        with self.assertRaises(ValidationError):
            try:
                FTLFolder(name=tv.FOLDER1_NAME).full_clean()
            except ValidationError as e:
                self.assertIn('org', str(e))
                raise

    def test_delete_document(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        # Create a custom document specific to this test because we don't want to delete the test pdf file.
        binary_f = tempfile.NamedTemporaryFile(dir=os.path.join(BASE_DIR, 'ftests', 'tools'), delete=False)
        binary_f.write(b'Hello world!')  # Actual content doesn't matter
        binary_f.close()

        thumbnail_f = tempfile.NamedTemporaryFile(dir=os.path.join(BASE_DIR, 'ftests', 'tools'), delete=False)
        thumbnail_f.write(b'Hello world!')  # Actual content doesn't matter
        thumbnail_f.close()

        document_to_be_deleted = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document to be deleted",
            binary=binary_f.name,
            thumbnail_binary=thumbnail_f.name
        )

        document_to_be_deleted.delete()

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=document_to_be_deleted.pid)

        # File has been deleted.
        self.assertTrue(not os.path.exists(binary_f.name))
        self.assertTrue(not os.path.exists(thumbnail_f.name))

    def test_delete_folders(self):
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        folder = setup_folder(org)
        folder_sub = setup_folder(org, parent=folder)
        document_1 = setup_document(org, user, binary=setup_temporary_file().name)
        document_2 = setup_document(org, user, folder, binary=setup_temporary_file().name)
        document_3 = setup_document(org, user, folder_sub, binary=setup_temporary_file().name)

        self.assertEqual(FTLDocument.objects.count(), 3)
        self.assertEqual(FTLFolder.objects.count(), 2)

        folder.delete()

        self.assertEqual(FTLDocument.objects.count(), 1)
        self.assertEqual(FTLFolder.objects.count(), 0)

        self.assertIsNotNone(FTLDocument.objects.get(pid=document_1.pid))

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=document_2.pid)

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=document_3.pid)
