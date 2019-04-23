import os
import tempfile

from rest_framework import status
from rest_framework.test import APITestCase

import core
from core.models import FTLDocument
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import BASE_DIR


class DocumentsTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document",
            binary='uploads/test.pdf',
        )

        self.doc_bis = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document 2",
            binary='uploads/test.pdf',
        )

        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

    def test_list_documents(self):
        ftl_document = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document.pid)

        ftl_document_bis = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document_bis.pid)

        client_get = self.client.get('/app/api/v1/documents/', format='json')

        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get['Content-Type'], 'application/json')
        self.assertEqual(client_get.data['count'], 2)

    def test_list_documents_order(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document_second.pid)

        client_get = self.client.get('/app/api/v1/documents/', format='json')

        # First document should be the last one uploaded.
        client_doc = client_get.data['results'][0]
        self.assertEqual(client_doc['pid'], str(ftl_document_second.pid))
        self.assertEqual(client_doc['title'], ftl_document_second.title)
        self.assertEqual(client_doc['note'], ftl_document_second.note)
        self.assertEqual(client_doc['ftl_folder'], ftl_document_second.ftl_folder)

        client_doc = client_get.data['results'][1]
        self.assertEqual(client_doc['pid'], str(ftl_document_first.pid))
        self.assertEqual(client_doc['title'], ftl_document_first.title)
        self.assertEqual(client_doc['note'], ftl_document_first.note)
        self.assertEqual(client_doc['ftl_folder'], ftl_document_first.ftl_folder)

    def test_get_document(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        client_get = self.client.get('/app/api/v1/documents/' + str(self.doc.pid), format='json')

        # First document should be the last one uploaded.
        client_doc = client_get.data
        self.assertEqual(client_doc['pid'], str(ftl_document_first.pid))
        self.assertEqual(client_doc['title'], ftl_document_first.title)
        self.assertEqual(client_doc['note'], ftl_document_first.note)
        self.assertEqual(client_doc['ftl_folder'], ftl_document_first.ftl_folder)

    def test_delete_document(self):
        # Create a custom document specific to this test because we don't want to delete the test pdf file.
        binary_f = tempfile.NamedTemporaryFile(dir=os.path.join(BASE_DIR, 'uploads'), delete=False)
        binary_f.write(b'Hello world!')  # Actual content doesn't matter
        binary_f.close()

        document_to_be_deleted = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document to be deleted",
            binary=binary_f.name,
        )

        client_delete = self.client.delete('/app/api/v1/documents/' + str(document_to_be_deleted.pid))
        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=document_to_be_deleted.pid)

        # File has been deleted.
        self.assertTrue(not os.path.exists(binary_f.name))

    def test_upload_document(self):
        # Create a custom document specific to this test because we don't want to delete the test pdf file.
        binary_f = tempfile.NamedTemporaryFile(dir=os.path.join(BASE_DIR, 'uploads'), delete=False)
        binary_f.write(b'Hello world!')
        binary_f.close()

        with open(binary_f.name) as fp:
            client_post = self.client.post('/app/api/v1/documents/upload', {'json': '{}', 'file': fp})

        self.assertEqual(client_post.status_code, status.HTTP_200_OK)

        client_doc = client_post.data
        self.assertIsNotNone(client_doc['pid'])
        self.assertIsNotNone(client_doc['title'])
        self.assertEqual(client_doc['note'], '')
        self.assertEqual(client_doc['ftl_folder'], None)
