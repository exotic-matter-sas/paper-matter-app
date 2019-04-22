from rest_framework import status
from rest_framework.test import APITestCase

from core.models import FTLDocument
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class DocumentsTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # setup_authenticated_session(self.client, self.org, self.user)

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

    def test_list_documents(self):
        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

        ftl_document = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document.pid)

        ftl_document_bis = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document_bis.pid)

        client_get = self.client.get('/app/api/v1/documents', format='json', follow=True)

        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get['Content-Type'], 'application/json')
        self.assertEqual(client_get.data['count'], 2)

    def test_list_documents_order(self):
        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document_second.pid)

        client_get = self.client.get('/app/api/v1/documents', format='json', follow=True)

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
        pass
