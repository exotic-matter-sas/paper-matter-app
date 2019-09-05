import json
import os
import tempfile
from unittest.mock import patch

from django.contrib import messages
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

import core
from core.models import FTLDocument, FTLFolder
from core.processing.ftl_processing import FTLDocumentProcessing
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftl.enums import FTLStorages, FTLPlugins
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

        client_get = self.client.get('/app/api/v1/documents', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get['Content-Type'], 'application/json')
        self.assertEqual(client_get.data['count'], 2)
        self.assertEqual(len(client_get.data['results']), 2)

    def test_list_documents_order_recent(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)

        client_get = self.client.get('/app/api/v1/documents', format='json')
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

    def test_list_documents_order_older(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)

        client_get = self.client.get('/app/api/v1/documents?ordering=created', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data['results'][0]
        self.assertEqual(client_doc_1['pid'], str(ftl_document_first.pid))

        client_doc_2 = client_get.data['results'][1]
        self.assertEqual(client_doc_2['pid'], str(ftl_document_second.pid))

    def test_list_documents_order_az(self):
        FTLDocument.objects.all().delete()

        doc_efg = setup_document(self.org, self.user, title='EFG')
        doc_bcd = setup_document(self.org, self.user, title='BCD')
        doc_abc = setup_document(self.org, self.user, title='ABC')

        ftl_document_first = FTLDocument.objects.get(pid=doc_abc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=doc_bcd.pid)
        ftl_document_third = FTLDocument.objects.get(pid=doc_efg.pid)

        client_get = self.client.get('/app/api/v1/documents?ordering=title', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data['results'][0]
        self.assertEqual(client_doc_1['pid'], str(ftl_document_first.pid))
        self.assertEqual(client_doc_1['title'], ftl_document_first.title)

        client_doc_2 = client_get.data['results'][1]
        self.assertEqual(client_doc_2['pid'], str(ftl_document_second.pid))
        self.assertEqual(client_doc_2['title'], ftl_document_second.title)

        client_doc_3 = client_get.data['results'][2]
        self.assertEqual(client_doc_3['pid'], str(ftl_document_third.pid))
        self.assertEqual(client_doc_3['title'], ftl_document_third.title)

    def test_list_documents_order_za(self):
        FTLDocument.objects.all().delete()

        doc_efg = setup_document(self.org, self.user, title='EFG')
        doc_bcd = setup_document(self.org, self.user, title='BCD')
        doc_abc = setup_document(self.org, self.user, title='ABC')

        ftl_document_first = FTLDocument.objects.get(pid=doc_efg.pid)
        ftl_document_second = FTLDocument.objects.get(pid=doc_bcd.pid)
        ftl_document_third = FTLDocument.objects.get(pid=doc_abc.pid)

        client_get = self.client.get('/app/api/v1/documents?ordering=-title', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data['results'][0]
        self.assertEqual(client_doc_1['pid'], str(ftl_document_first.pid))
        self.assertEqual(client_doc_1['title'], ftl_document_first.title)

        client_doc_2 = client_get.data['results'][1]
        self.assertEqual(client_doc_2['pid'], str(ftl_document_second.pid))
        self.assertEqual(client_doc_2['title'], ftl_document_second.title)

        client_doc_3 = client_get.data['results'][2]
        self.assertEqual(client_doc_3['pid'], str(ftl_document_third.pid))
        self.assertEqual(client_doc_3['title'], ftl_document_third.title)

    @patch.object(messages, 'success')
    def test_list_documents_added_by_another_user_of_same_org(self, messages_mocked):
        # First user logout and a second user of the same org login
        self.client.logout()
        setup_user(self.org, tv.USER2_EMAIL, tv.USER2_USERNAME, tv.USER2_PASS)
        self.client.login(username=tv.USER2_USERNAME, password=tv.USER2_PASS)

        client_get = self.client.get('/app/api/v1/documents', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get['Content-Type'], 'application/json')
        self.assertEqual(client_get.data['count'], 2)
        self.assertEqual(len(client_get.data['results']), 2)

    @patch.object(messages, 'success')
    def test_cant_list_documents_from_another_org(self, messages_mocked):
        # First user logout and a second user of the another org login
        self.client.logout()
        org2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)
        setup_user(org2, tv.USER2_EMAIL, tv.USER2_USERNAME, tv.USER2_PASS)
        self.client.login(username=tv.USER2_USERNAME, password=tv.USER2_PASS)

        client_get = self.client.get('/app/api/v1/documents', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get['Content-Type'], 'application/json')
        self.assertEqual(client_get.data['count'], 0)
        self.assertEqual(len(client_get.data['results']), 0)

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

    @override_settings(DEFAULT_FILE_STORAGE=FTLStorages.FILE_SYSTEM)
    def test_delete_document(self):
        # Create a custom document specific to this test because we don't want to delete the test pdf file.
        binary_f = tempfile.NamedTemporaryFile(dir=os.path.join(BASE_DIR, 'ftests', 'tools'), delete=False)
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

    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_document(self, mock_apply_processing):
        with open(os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf'), mode='rb') as fp:
            client_post = self.client.post('/app/api/v1/documents/upload', {'json': '{}', 'file': fp})
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        objects_get = FTLDocument.objects.get(pid=client_doc['pid'])

        self.assertEqual(str(objects_get.pid), client_doc['pid'])
        self.assertEqual(objects_get.title, client_doc['title'])
        self.assertEqual(objects_get.note, client_doc['note'])
        self.assertIsNone(objects_get.ftl_folder)

    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_doc_trigger_document_processing(self, mock_apply_processing):
        with open(os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf'), 'rb') as f:
            body_post = {'json': '{}', 'file': f}
            self.client.post('/app/api/v1/documents/upload', body_post)

        mock_apply_processing.assert_called_once()
        # Check argument is a FTLDocument
        call = mock_apply_processing.call_args_list[0]
        args, kwarg = call
        self.assertTrue(isinstance(args[0], FTLDocument))

    def test_document_in_folder(self):
        client_get = self.client.get(f'/app/api/v1/documents?level={self.first_level_folder.id}', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get.data['count'], 1)
        self.assertEqual(len(client_get.data['results']), 1)

        client_doc = client_get.data['results'][0]
        self.assertEqual(client_doc['pid'], str(self.doc_in_folder.pid))
        self.assertEqual(client_doc['title'], self.doc_in_folder.title)
        self.assertEqual(client_doc['note'], self.doc_in_folder.note)
        self.assertEqual(client_doc['ftl_folder'], self.first_level_folder.id)

    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_document_in_folder(self, mock_apply_processing):
        post_body = {'ftl_folder': self.first_level_folder.id}

        with open(os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf'), mode='rb') as fp:
            client_post = self.client.post('/app/api/v1/documents/upload', {'json': json.dumps(post_body), 'file': fp})
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        self.assertEqual(client_doc['ftl_folder'], self.first_level_folder.id)

        ftl_doc_from_db = FTLDocument.objects.get(pid=client_doc['pid'])
        self.assertEqual(str(ftl_doc_from_db.pid), client_doc['pid'])
        self.assertEqual(ftl_doc_from_db.title, client_doc['title'])
        self.assertEqual(ftl_doc_from_db.note, client_doc['note'])
        self.assertEqual(ftl_doc_from_db.ftl_folder, self.first_level_folder)

        client_get_level = self.client.get(f'/app/api/v1/documents?level={self.first_level_folder.id}', format='json')
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

    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_rename_document_reapply_tsvector_proc(self, mock_apply_processing):
        client_get = self.client.patch(f'/app/api/v1/documents/{self.doc.pid}',
                                       {'title': 'renamed'},
                                       format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # tsvector processing should be forced on rename
        mock_apply_processing.assert_called_once()
        call = mock_apply_processing.call_args_list[0]
        args, kwarg = call
        self.assertIn(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR, args[1])

    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_annotate_document_reapply_tsvector_proc(self, mock_apply_processing):
        client_get = self.client.patch(f'/app/api/v1/documents/{self.doc.pid}',
                                       {'note': 'reannoted'},
                                       format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # tsvector processing should be forced on rename
        mock_apply_processing.assert_called_once()
        call = mock_apply_processing.call_args_list[0]
        args, kwarg = call
        self.assertIn(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR, args[1])


class DocumentsSearchTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

    def test_list_documents_search_title(self):
        doc_to_search = setup_document(self.org, self.user, note='bingo!')

        search_result = self.client.get(f'/app/api/v1/documents?search={doc_to_search.title}', format='json')
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result['Content-Type'], 'application/json')
        self.assertEqual(search_result.data['count'], 1)
        self.assertEqual(len(search_result.data['results']), 1)
        self.assertEqual(search_result.data['results'][0]['note'], 'bingo!')

    def test_list_documents_search_note(self):
        doc_to_search = setup_document(self.org, self.user, title='bingo!')

        search_result = self.client.get(f'/app/api/v1/documents?search={doc_to_search.note}', format='json')
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result['Content-Type'], 'application/json')
        self.assertEqual(search_result.data['count'], 1)
        self.assertEqual(len(search_result.data['results']), 1)
        self.assertEqual(search_result.data['results'][0]['title'], 'bingo!')

    def test_list_documents_search_content_text(self):
        doc_to_search = setup_document(self.org, self.user, title='bingo!')

        search_result = self.client.get(f'/app/api/v1/documents?search={doc_to_search.content_text}', format='json')
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result['Content-Type'], 'application/json')
        self.assertEqual(search_result.data['count'], 1)
        self.assertEqual(len(search_result.data['results']), 1)
        self.assertEqual(search_result.data['results'][0]['title'], 'bingo!')


class FoldersTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.folder_root = setup_folder(self.org, name='First level folder')

        self.folder_root_subfolder = setup_folder(self.org, name='Second level folder', parent=self.folder_root)

        self.client.login(username=tv.USER1_USERNAME, password=tv.USER1_PASS)

    def test_folder_tree_root_level(self):
        client_get = self.client.get('/app/api/v1/folders', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data['id'], self.folder_root.id)
        self.assertEqual(client_data['name'], self.folder_root.name)
        self.assertIsNone(client_data['parent'])

    def test_folder_tree_root_subfolder(self):
        client_get = self.client.get(f'/app/api/v1/folders?level={self.folder_root.id}', format='json')
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data['id'], self.folder_root_subfolder.id)
        self.assertEqual(client_data['name'], self.folder_root_subfolder.name)
        self.assertEqual(client_data['parent'], self.folder_root.id)

    def test_create_folder(self):
        client_post = self.client.post('/app/api/v1/folders', {'name': 'Folder created'}, format='json')
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        objects_get = FTLFolder.objects.get(id=client_post.data['id'])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data['id'])
        self.assertEqual(objects_get.name, client_post.data['name'])
        self.assertIsNone(client_post.data['parent'])

    def test_create_folder_in_folder(self):
        client_post = self.client.post('/app/api/v1/folders',
                                       {'name': 'Folder created', 'parent': self.folder_root.id}, format='json')
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(client_post.data['parent'], self.folder_root.id)

        objects_get = FTLFolder.objects.get(id=client_post.data['id'])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data['id'])
        self.assertEqual(objects_get.name, client_post.data['name'])
        self.assertEqual(objects_get.parent, self.folder_root)

    def test_delete_folder(self):
        folder_to_be_delete = setup_folder(self.org, name='Folder to delete')

        client_delete = self.client.delete(f'/app/api/v1/folders/{folder_to_be_delete.id}')

        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLFolder.DoesNotExist):
            FTLFolder.objects.get(id=folder_to_be_delete.id)

    def test_create_same_folder_name(self):
        # We try to create a folder with a name already used in setUp
        response = self.client.post('/app/api/v1/folders',
                                    {'name': self.folder_root.name}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'folder_name_unique_for_org_level')


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(self.org, self.user)
        self.doc_bis = setup_document(self.org, self.user, title=tv.DOCUMENT2_TITLE)

        self.first_level_folder = setup_folder(self.org, name='First level folder')

        self.doc_in_folder = setup_document(self.org, self.user, title='Document in folder',
                                            ftl_folder=self.first_level_folder)

    def test_get_token(self):
        response = self.client.post('/app/api/token',
                                    {'username': tv.USER1_USERNAME, 'password': tv.USER1_PASS},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

    def test_refresh_token(self):
        response_token = self.client.post('/app/api/token',
                                          {'username': tv.USER1_USERNAME, 'password': tv.USER1_PASS},
                                          format='json')

        response = self.client.post('/app/api/token/refresh',
                                    {'refresh': response_token.data['refresh']},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['access'])

    def test_use_token(self):
        response_token = self.client.post('/app/api/token',
                                          {'username': tv.USER1_USERNAME, 'password': tv.USER1_PASS},
                                          format='json')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response_token.data["access"]}')
        response = self.client.get('/app/api/v1/documents')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['count'])
