import json
import os
import tempfile

from rest_framework import status
from rest_framework.test import APITestCase

import core
from core.models import FTLDocument, FTLFolder
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftl.settings import BASE_DIR


class DocumentsTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(self.org, self.user)
        self.doc_bis = setup_document(self.org, self.user, title=tv.DOCUMENT2_TITLE)

        self.first_level_folder = setup_folder(self.org, name='First level folder')

        self.doc_in_folder = setup_document(self.org, self.user, title='Document in folder',
                                            ftl_folder=self.first_level_folder)

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
        self.assertEqual(len(client_get.data['results']), 2)

    def test_list_documents_order(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)

        client_get = self.client.get('/app/api/v1/documents/', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # First document should be the last one uploaded. (default sort: recent to old)
        client_doc_1 = client_get.data['results'][0]
        self.assertEqual(client_doc_1['pid'], str(ftl_document_second.pid))
        self.assertEqual(client_doc_1['title'], ftl_document_second.title)
        self.assertEqual(client_doc_1['note'], ftl_document_second.note)
        self.assertEqual(client_doc_1['ftl_folder'], ftl_document_second.ftl_folder)

        client_doc_2 = client_get.data['results'][1]
        self.assertEqual(client_doc_2['pid'], str(ftl_document_first.pid))
        self.assertEqual(client_doc_2['title'], ftl_document_first.title)
        self.assertEqual(client_doc_2['note'], ftl_document_first.note)
        self.assertEqual(client_doc_2['ftl_folder'], ftl_document_first.ftl_folder)

    def test_get_document(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        client_get = self.client.get(f'/app/api/v1/documents/{str(self.doc.pid)}', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # First document should be the last one uploaded. (default sort: recent to old)
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

        client_delete = self.client.delete(f'/app/api/v1/documents/{str(document_to_be_deleted.pid)}')
        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=document_to_be_deleted.pid)

        # File has been deleted.
        self.assertTrue(not os.path.exists(binary_f.name))

    def test_upload_document(self):
        with open(os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf'), mode='rb') as fp:
            client_post = self.client.post('/app/api/v1/documents/upload', {'json': '{}', 'file': fp})
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        objects_get = FTLDocument.objects.get(pid=client_doc['pid'])

        self.assertEqual(str(objects_get.pid), client_doc['pid'])
        self.assertEqual(objects_get.title, client_doc['title'])
        self.assertEqual(objects_get.note, client_doc['note'])
        self.assertIsNone(objects_get.ftl_folder)

    def test_document_in_folder(self):
        client_get = self.client.get(f'/app/api/v1/documents/?level={self.first_level_folder.id}', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get.data['count'], 1)
        self.assertEqual(len(client_get.data['results']), 1)

        client_doc = client_get.data['results'][0]
        self.assertEqual(client_doc['pid'], str(self.doc_in_folder.pid))
        self.assertEqual(client_doc['title'], self.doc_in_folder.title)
        self.assertEqual(client_doc['note'], self.doc_in_folder.note)
        self.assertEqual(client_doc['ftl_folder'], self.first_level_folder.id)

    def test_upload_document_in_folder(self):
        post_body = {'ftl_folder': self.first_level_folder.id}

        with open(os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf'), mode='rb') as fp:
            client_post = self.client.post('/app/api/v1/documents/upload', {'json': json.dumps(post_body), 'file': fp})
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        self.assertEqual(client_doc['ftl_folder'], self.first_level_folder.id)

        ftl_doc_from_db = FTLDocument.objects.get(pid=client_doc['pid'])
        self.assertEqual(str(ftl_doc_from_db.pid), client_doc['pid'])
        self.assertEqual(ftl_doc_from_db.title, client_doc['title'])
        self.assertEqual(ftl_doc_from_db.note, client_doc['note'])
        self.assertEqual(ftl_doc_from_db.ftl_folder, self.first_level_folder)

        client_get_level = self.client.get(f'/app/api/v1/documents/?level={self.first_level_folder.id}', format='json')
        self.assertEqual(client_get_level.status_code, status.HTTP_200_OK)
        # There should be 2 documents (one from setUp and the new uploaded one)
        self.assertEqual(client_get_level.data['count'], 2)
        self.assertEqual(len(client_get_level.data['results']), 2)

        # The latest document should be the one we just uploaded.
        client_doc_level = client_get_level.data['results'][0]
        self.assertEqual(client_doc_level['pid'], client_doc['pid'])
        self.assertEqual(client_doc_level['title'], client_doc['title'])
        self.assertEqual(client_doc_level['note'], client_doc['note'])
        self.assertEqual(client_doc_level['ftl_folder'], client_doc['ftl_folder'])


class FoldersTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.folder_root = setup_folder(self.org, name='First level folder')

        self.folder_root_subfolder = setup_folder(self.org, name='Second level folder', parent=self.folder_root)

        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

    def test_folder_tree_root_level(self):
        client_get = self.client.get('/app/api/v1/folders/', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data['id'], self.folder_root.id)
        self.assertEqual(client_data['name'], self.folder_root.name)
        self.assertIsNone(client_data['parent'])

    def test_folder_tree_root_subfolder(self):
        client_get = self.client.get(f'/app/api/v1/folders/?level={self.folder_root.id}', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data['id'], self.folder_root_subfolder.id)
        self.assertEqual(client_data['name'], self.folder_root_subfolder.name)
        self.assertEqual(client_data['parent'], self.folder_root.id)

    def test_create_folder(self):
        client_post = self.client.post('/app/api/v1/folders/', {'name': 'Folder created'}, format='json')
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        objects_get = FTLFolder.objects.get(id=client_post.data['id'])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data['id'])
        self.assertEqual(objects_get.name, client_post.data['name'])
        self.assertIsNone(client_post.data['parent'])

    def test_create_folder_in_folder(self):
        client_post = self.client.post('/app/api/v1/folders/',
                                       {'name': 'Folder created', 'parent': self.folder_root.id}, format='json')
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(client_post.data['parent'], self.folder_root.id)

        objects_get = FTLFolder.objects.get(id=client_post.data['id'])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data['id'])
        self.assertEqual(objects_get.name, client_post.data['name'])
        self.assertEqual(objects_get.parent, self.folder_root)
