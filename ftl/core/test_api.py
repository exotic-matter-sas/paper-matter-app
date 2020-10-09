#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import json
import os
from contextlib import contextmanager
from unittest import mock
from unittest.mock import patch
from uuid import UUID

from django.contrib import messages
from django.db import DEFAULT_DB_ALIAS
from django.http import HttpRequest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

import core
from core.models import FTLDocument, FTLFolder, FTLDocumentSharing
from core.tasks import apply_ftl_processing
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_folder,
    setup_temporary_file,
    setup_document_share,
)
from ftl import celery
from ftl.enums import FTLStorages, FTLPlugins
from ftl.settings import BASE_DIR


class DocumentsTests(APITestCase):
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

        self.client.login(
            request=HttpRequest(), email=tv.USER1_EMAIL, password=tv.USER1_PASS
        )

    def test_list_documents(self):
        ftl_document = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document.pid)

        ftl_document_bis = FTLDocument.objects.get(pid=self.doc_bis.pid)
        self.assertIsNotNone(ftl_document_bis.pid)

        client_get = self.client.get("/app/api/v1/documents", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get["Content-Type"], "application/json")
        self.assertEqual(client_get.data["count"], 2)
        self.assertEqual(len(client_get.data["results"]), 2)

    def test_list_document_flat(self):
        client_get = self.client.get("/app/api/v1/documents?flat=true", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get["Content-Type"], "application/json")
        self.assertEqual(client_get.data["count"], 3)
        self.assertEqual(len(client_get.data["results"]), 3)

        list_docs_pid = [doc["pid"] for doc in client_get.data["results"]]

        self.assertIn(str(self.doc.pid), list_docs_pid)
        self.assertIn(str(self.doc_bis.pid), list_docs_pid)
        self.assertIn(str(self.doc_in_folder.pid), list_docs_pid)

    def test_list_document_flat_with_folder(self):
        client_get = self.client.get(
            f"/app/api/v1/documents?flat=true&level={self.first_level_folder.id}",
            format="json",
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get["Content-Type"], "application/json")
        self.assertEqual(client_get.data["count"], 1)
        self.assertEqual(len(client_get.data["results"]), 1)

        list_docs_pid = [doc["pid"] for doc in client_get.data["results"]]

        self.assertNotIn(str(self.doc.pid), list_docs_pid)
        self.assertNotIn(str(self.doc_bis.pid), list_docs_pid)
        self.assertIn(str(self.doc_in_folder.pid), list_docs_pid)

    def test_list_documents_order_recent(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)

        client_get = self.client.get("/app/api/v1/documents", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # First document should be the last one uploaded. (default sort: recent to old)
        client_doc_1 = client_get.data["results"][0]
        self.assertEqual(client_doc_1["pid"], str(ftl_document_second.pid))
        self.assertEqual(client_doc_1["title"], ftl_document_second.title)
        self.assertEqual(client_doc_1["note"], ftl_document_second.note)
        self.assertEqual(client_doc_1["ftl_folder"], ftl_document_second.ftl_folder)

        client_doc_2 = client_get.data["results"][1]
        self.assertEqual(client_doc_2["pid"], str(ftl_document_first.pid))
        self.assertEqual(client_doc_2["title"], ftl_document_first.title)
        self.assertEqual(client_doc_2["note"], ftl_document_first.note)
        self.assertEqual(client_doc_2["ftl_folder"], ftl_document_first.ftl_folder)

    def test_list_documents_order_older(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=self.doc_bis.pid)

        client_get = self.client.get(
            "/app/api/v1/documents?ordering=created", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data["results"][0]
        self.assertEqual(client_doc_1["pid"], str(ftl_document_first.pid))

        client_doc_2 = client_get.data["results"][1]
        self.assertEqual(client_doc_2["pid"], str(ftl_document_second.pid))

    def test_list_documents_order_az(self):
        FTLDocument.objects.all().delete()

        doc_efg = setup_document(self.org, self.user, title="EFG")
        doc_bcd = setup_document(self.org, self.user, title="BCD")
        doc_abc = setup_document(self.org, self.user, title="ABC")

        ftl_document_first = FTLDocument.objects.get(pid=doc_abc.pid)
        ftl_document_second = FTLDocument.objects.get(pid=doc_bcd.pid)
        ftl_document_third = FTLDocument.objects.get(pid=doc_efg.pid)

        client_get = self.client.get(
            "/app/api/v1/documents?ordering=title", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data["results"][0]
        self.assertEqual(client_doc_1["pid"], str(ftl_document_first.pid))
        self.assertEqual(client_doc_1["title"], ftl_document_first.title)

        client_doc_2 = client_get.data["results"][1]
        self.assertEqual(client_doc_2["pid"], str(ftl_document_second.pid))
        self.assertEqual(client_doc_2["title"], ftl_document_second.title)

        client_doc_3 = client_get.data["results"][2]
        self.assertEqual(client_doc_3["pid"], str(ftl_document_third.pid))
        self.assertEqual(client_doc_3["title"], ftl_document_third.title)

    def test_list_documents_order_za(self):
        FTLDocument.objects.all().delete()

        doc_efg = setup_document(self.org, self.user, title="EFG")
        doc_bcd = setup_document(self.org, self.user, title="BCD")
        doc_abc = setup_document(self.org, self.user, title="ABC")

        ftl_document_first = FTLDocument.objects.get(pid=doc_efg.pid)
        ftl_document_second = FTLDocument.objects.get(pid=doc_bcd.pid)
        ftl_document_third = FTLDocument.objects.get(pid=doc_abc.pid)

        client_get = self.client.get(
            "/app/api/v1/documents?ordering=-title", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc_1 = client_get.data["results"][0]
        self.assertEqual(client_doc_1["pid"], str(ftl_document_first.pid))
        self.assertEqual(client_doc_1["title"], ftl_document_first.title)

        client_doc_2 = client_get.data["results"][1]
        self.assertEqual(client_doc_2["pid"], str(ftl_document_second.pid))
        self.assertEqual(client_doc_2["title"], ftl_document_second.title)

        client_doc_3 = client_get.data["results"][2]
        self.assertEqual(client_doc_3["pid"], str(ftl_document_third.pid))
        self.assertEqual(client_doc_3["title"], ftl_document_third.title)

    @patch.object(messages, "success")
    def test_list_documents_added_by_another_user_of_same_org(self, messages_mocked):
        # First user logout and a second user of the same org login
        self.client.logout()
        setup_user(self.org, tv.USER2_EMAIL, tv.USER2_PASS)
        self.client.login(
            request=HttpRequest(), email=tv.USER2_EMAIL, password=tv.USER2_PASS
        )

        client_get = self.client.get("/app/api/v1/documents", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get["Content-Type"], "application/json")
        self.assertEqual(client_get.data["count"], 2)
        self.assertEqual(len(client_get.data["results"]), 2)

    @patch.object(messages, "success")
    def test_cant_list_documents_from_another_org(self, messages_mocked):
        # First user logout and a second user of the another org login
        self.client.logout()
        org2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)
        setup_user(org2, tv.USER2_EMAIL, tv.USER2_PASS)
        self.client.login(
            request=HttpRequest(), email=tv.USER2_EMAIL, password=tv.USER2_PASS
        )

        client_get = self.client.get("/app/api/v1/documents", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get["Content-Type"], "application/json")
        self.assertEqual(client_get.data["count"], 0)
        self.assertEqual(len(client_get.data["results"]), 0)

    def test_get_document(self):
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        client_get = self.client.get(
            f"/app/api/v1/documents/{str(self.doc.pid)}", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # First document should be the last one uploaded. (default sort: recent to old)
        client_doc = client_get.data
        self.assertEqual(client_doc["pid"], str(ftl_document_first.pid))
        self.assertEqual(client_doc["title"], ftl_document_first.title)
        self.assertEqual(client_doc["note"], ftl_document_first.note)
        self.assertEqual(client_doc["ftl_folder"], ftl_document_first.ftl_folder)

    @override_settings(DEFAULT_FILE_STORAGE=FTLStorages.FILE_SYSTEM)
    @patch.object(celery.app, "send_task")
    def test_delete_document(self, mock_send_task_delete_document):
        binary_f = setup_temporary_file().name
        document_to_be_deleted = FTLDocument.objects.create(
            org=self.org,
            ftl_user=self.user,
            title="Test document to be deleted",
            binary=binary_f,  # We don't want to delete the test pdf file
        )

        client_delete = self.client.delete(
            f"/app/api/v1/documents/{str(document_to_be_deleted.pid)}"
        )
        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        document_marked_as_deleted = FTLDocument.objects.get(
            pid=document_to_be_deleted.pid
        )
        self.assertTrue(document_marked_as_deleted.deleted)

        # File has not been deleted.
        self.assertTrue(os.path.exists(binary_f))

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        objects_get = FTLDocument.objects.get(pid=client_doc["pid"])

        self.assertEqual(str(objects_get.pid), client_doc["pid"])
        self.assertEqual(objects_get.title, client_doc["title"])
        self.assertEqual(objects_get.note, client_doc["note"])
        self.assertIsNone(objects_get.ftl_folder)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_correct_size(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        objects_get = FTLDocument.objects.get(pid=client_doc["pid"])

        self.assertEqual(objects_get.size, 20247)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_correct_md5(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        objects_get = FTLDocument.objects.get(pid=client_doc["pid"])

        self.assertEqual(objects_get.md5, "2b0d9bcba3913d2d26b364630dab4c4b")

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_incorrect_md5(self, mock_apply_processing):
        initial_docs_count = FTLDocument.objects.count()

        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload",
                {"json": '{"md5": "hi there!"}', "file": fp},
            )

        self.assertEqual(client_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(client_post.data["code"], "ftl_document_md5_mismatch")

        final_docs_count = FTLDocument.objects.count()

        self.assertEqual(
            initial_docs_count,
            final_docs_count,
            "No document should have been added as upload fail",
        )

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_doc_with_creation_date(self, mock_apply_processing):
        creation_date = "2019-11-15T08:54:33.361913+00:00"
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            "rb",
        ) as f:
            data = {"created": creation_date}
            body_post = {"json": json.dumps(data), "file": f}
            response = self.client.post("/app/api/v1/documents/upload", body_post)

        upload_doc = response.data
        objects_get = FTLDocument.objects.get(pid=upload_doc["pid"])
        self.assertEqual(creation_date, objects_get.created.isoformat())

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_doc_with_title(self, mock_apply_processing):
        title = "My document 123"
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            "rb",
        ) as f:
            data = {"title": title}
            body_post = {"json": json.dumps(data), "file": f}
            response = self.client.post("/app/api/v1/documents/upload", body_post)

        upload_doc = response.data
        objects_get = FTLDocument.objects.get(pid=upload_doc["pid"])
        self.assertEqual(title, objects_get.title)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_doc_with_note(self, mock_apply_processing):
        note = "My document note 123"
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            "rb",
        ) as f:
            data = {"note": note}
            body_post = {"json": json.dumps(data), "file": f}
            response = self.client.post("/app/api/v1/documents/upload", body_post)

        upload_doc = response.data
        objects_get = FTLDocument.objects.get(pid=upload_doc["pid"])
        self.assertEqual(note, objects_get.note)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_wrong_format(self, mock_apply_processing):
        with open(
            os.path.join(
                BASE_DIR, "ftests", "tools", "test_documents", "wrong-format.exe"
            ),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(
            client_post.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_wrong_format_fake_document(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "fake.dok"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(
            client_post.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_docx(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "word.docx"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_xlsx(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "excel.xlsx"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_txt(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "hello.txt"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload", {"json": "{}", "file": fp}
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_doc_trigger_document_processing(self, mock_apply_processing):
        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            "rb",
        ) as f:
            with execute_on_commit():
                body_post = {"json": "{}", "file": f}
                self.client.post("/app/api/v1/documents/upload", body_post)

        mock_apply_processing.assert_called_once()
        # Check argument is a FTLDocument
        args, kwarg = mock_apply_processing.call_args_list[0]
        self.assertTrue(isinstance(args[0], UUID))
        self.assertTrue(isinstance(args[1], int))
        self.assertTrue(isinstance(args[2], int))
        self.assertTrue(isinstance(kwarg["force"], list))

    def test_document_in_folder(self):
        client_get = self.client.get(
            f"/app/api/v1/documents?level={self.first_level_folder.id}", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(client_get.data["count"], 1)
        self.assertEqual(len(client_get.data["results"]), 1)

        client_doc = client_get.data["results"][0]
        self.assertEqual(client_doc["pid"], str(self.doc_in_folder.pid))
        self.assertEqual(client_doc["title"], self.doc_in_folder.title)
        self.assertEqual(client_doc["note"], self.doc_in_folder.note)
        self.assertEqual(client_doc["ftl_folder"], self.first_level_folder.id)

    @patch.object(apply_ftl_processing, "delay")
    def test_upload_document_in_folder(self, mock_apply_processing):
        post_body = {"ftl_folder": self.first_level_folder.id}

        with open(
            os.path.join(BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"),
            mode="rb",
        ) as fp:
            client_post = self.client.post(
                "/app/api/v1/documents/upload",
                {"json": json.dumps(post_body), "file": fp},
            )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        client_doc = client_post.data
        self.assertEqual(client_doc["ftl_folder"], self.first_level_folder.id)

        ftl_doc_from_db = FTLDocument.objects.get(pid=client_doc["pid"])
        self.assertEqual(str(ftl_doc_from_db.pid), client_doc["pid"])
        self.assertEqual(ftl_doc_from_db.title, client_doc["title"])
        self.assertEqual(ftl_doc_from_db.note, client_doc["note"])
        self.assertEqual(ftl_doc_from_db.ftl_folder, self.first_level_folder)

        client_get_level = self.client.get(
            f"/app/api/v1/documents?level={self.first_level_folder.id}", format="json"
        )
        self.assertEqual(client_get_level.status_code, status.HTTP_200_OK)
        # There should be 2 documents (one from setUp and the new uploaded one)
        self.assertEqual(client_get_level.data["count"], 2)
        self.assertEqual(len(client_get_level.data["results"]), 2)

        # The latest document should be the one we just uploaded.
        client_doc_level = client_get_level.data["results"][0]
        self.assertEqual(client_doc_level["pid"], client_doc["pid"])
        self.assertEqual(client_doc_level["title"], client_doc["title"])
        self.assertEqual(client_doc_level["note"], client_doc["note"])
        self.assertEqual(client_doc_level["ftl_folder"], client_doc["ftl_folder"])

    @patch.object(apply_ftl_processing, "delay")
    def test_rename_document_reapply_tsvector_proc(self, mock_apply_processing):
        with execute_on_commit():
            client_get = self.client.patch(
                f"/app/api/v1/documents/{self.doc.pid}",
                {"title": "renamed"},
                format="json",
            )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # tsvector processing should be forced on rename
        mock_apply_processing.assert_called_once()
        args, kwarg = mock_apply_processing.call_args_list[0]
        self.assertIn(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR, kwarg["force"])

    @patch.object(apply_ftl_processing, "delay")
    def test_annotate_document_reapply_tsvector_proc(self, mock_apply_processing):
        with execute_on_commit():
            client_get = self.client.patch(
                f"/app/api/v1/documents/{self.doc.pid}",
                {"note": "reannoted"},
                format="json",
            )

        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        # tsvector processing should be forced on rename
        mock_apply_processing.assert_called_once()
        args, kwarg = mock_apply_processing.call_args_list[0]
        self.assertIn(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR, kwarg["force"])


class DocumentsSearchTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.client.login(
            request=HttpRequest(), email=tv.USER1_EMAIL, password=tv.USER1_PASS
        )

    def test_list_documents_search_title(self):
        doc_to_search = setup_document(self.org, self.user, note="bingo!")

        search_result = self.client.get(
            f"/app/api/v1/documents?search={doc_to_search.title}", format="json"
        )
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result["Content-Type"], "application/json")
        self.assertEqual(search_result.data["count"], 1)
        self.assertEqual(len(search_result.data["results"]), 1)
        self.assertEqual(search_result.data["results"][0]["note"], "bingo!")

    def test_list_documents_search_note(self):
        doc_to_search = setup_document(self.org, self.user, title="bingo!")

        search_result = self.client.get(
            f"/app/api/v1/documents?search={doc_to_search.note}", format="json"
        )
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result["Content-Type"], "application/json")
        self.assertEqual(search_result.data["count"], 1)
        self.assertEqual(len(search_result.data["results"]), 1)
        self.assertEqual(search_result.data["results"][0]["title"], "bingo!")

    def test_list_documents_search_content_text(self):
        doc_to_search = setup_document(self.org, self.user, title="bingo!")

        search_result = self.client.get(
            f"/app/api/v1/documents?search={doc_to_search.content_text}", format="json"
        )
        self.assertEqual(search_result.status_code, status.HTTP_200_OK)
        self.assertEqual(search_result["Content-Type"], "application/json")
        self.assertEqual(search_result.data["count"], 1)
        self.assertEqual(len(search_result.data["results"]), 1)
        self.assertEqual(search_result.data["results"][0]["title"], "bingo!")


class DocumentSharingTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(self.org, self.user)
        self.doc_bis = setup_document(self.org, self.user, title=tv.DOCUMENT2_TITLE)

        self.client.login(
            request=HttpRequest(), email=tv.USER1_EMAIL, password=tv.USER1_PASS
        )

    def test_share_document(self):
        client_post = self.client.post(
            f"/app/api/v1/documents/{self.doc.pid}/share", format="json"
        )

        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)
        client_doc_share = client_post.data
        self.assertIsNotNone(client_doc_share["pid"])
        self.assertIsNotNone(client_doc_share["public_url"])
        self.assertIn(
            f"/app/share/{client_doc_share['pid']}", client_doc_share["public_url"]
        )
        ftl_document_sharing = FTLDocumentSharing.objects.get(
            pid=client_doc_share["pid"]
        )
        self.assertEqual(ftl_document_sharing.ftl_doc, self.doc)

    def test_get_document_share_links(self):
        share_doc = setup_document_share(self.doc)

        client_get = self.client.get(
            f"/app/api/v1/documents/{self.doc.pid}/share", format="json"
        )

        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        client_doc_shares = client_get.data
        self.assertEqual(client_doc_shares["count"], 1)
        self.assertEqual(client_doc_shares["results"][0]["pid"], str(share_doc.pid))

    def test_update_document_share_link(self):
        share_doc = setup_document_share(self.doc)

        client_patch = self.client.patch(
            f"/app/api/v1/documents/{self.doc.pid}/share/{share_doc.pid}",
            {"note": "fakeNote", "expire_at": "2019-11-18T00:42:42.242424Z"},
            format="json",
        )

        self.assertEqual(client_patch.status_code, status.HTTP_200_OK)
        client_doc_shares = client_patch.data
        self.assertEqual(client_doc_shares["pid"], str(share_doc.pid))
        self.assertEqual(client_doc_shares["note"], "fakeNote")
        self.assertEqual(client_doc_shares["expire_at"], "2019-11-18T00:42:42.242424Z")

    def test_unshare_document(self):
        share_doc = setup_document_share(self.doc)

        client_delete = self.client.delete(
            f"/app/api/v1/documents/{self.doc.pid}/share/{share_doc.pid}",
            format="json",
        )

        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLDocumentSharing.DoesNotExist):
            FTLDocumentSharing.objects.get(pid=share_doc.pid)

    def test_cant_share_not_owned_doc(self):
        org_bis = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        admin_bis = setup_admin(org_bis, tv.ADMIN2_EMAIL)
        doc_bis = setup_document(org_bis, admin_bis)

        client_post = self.client.post(
            f"/app/api/v1/documents/{doc_bis.pid}/share", format="json"
        )

        self.assertEqual(client_post.status_code, status.HTTP_404_NOT_FOUND)

    def test_cant_get_shares_for_not_owned_doc(self):
        org_bis = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        admin_bis = setup_admin(org_bis, tv.ADMIN2_EMAIL)
        doc_bis = setup_document(org_bis, admin_bis)
        share_doc_bis = setup_document_share(doc_bis)

        client_get = self.client.get(
            f"/app/api/v1/documents/{share_doc_bis.pid}/share", format="json"
        )

        self.assertEqual(client_get.status_code, status.HTTP_404_NOT_FOUND)


class FoldersTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.folder_root = setup_folder(self.org, name="First level folder")

        self.folder_root_subfolder = setup_folder(
            self.org, name="Second level folder", parent=self.folder_root
        )

        self.client.login(
            request=HttpRequest(), email=tv.USER1_EMAIL, password=tv.USER1_PASS
        )

    def test_folder_tree_root_level(self):
        client_get = self.client.get("/app/api/v1/folders", format="json")
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data["id"], self.folder_root.id)
        self.assertEqual(client_data["name"], self.folder_root.name)
        self.assertIsNone(client_data["parent"])

    def test_folder_tree_root_subfolder(self):
        client_get = self.client.get(
            f"/app/api/v1/folders?level={self.folder_root.id}", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_get.data), 1)

        client_data = client_get.data[0]
        self.assertEqual(client_data["id"], self.folder_root_subfolder.id)
        self.assertEqual(client_data["name"], self.folder_root_subfolder.name)
        self.assertEqual(client_data["parent"], self.folder_root.id)

    def test_create_folder(self):
        client_post = self.client.post(
            "/app/api/v1/folders", {"name": "Folder created"}, format="json"
        )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)

        objects_get = FTLFolder.objects.get(id=client_post.data["id"])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data["id"])
        self.assertEqual(objects_get.name, client_post.data["name"])
        self.assertIsNone(client_post.data["parent"])

    def test_create_folder_in_folder(self):
        client_post = self.client.post(
            "/app/api/v1/folders",
            {"name": "Folder created", "parent": self.folder_root.id},
            format="json",
        )
        self.assertEqual(client_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(client_post.data["parent"], self.folder_root.id)

        objects_get = FTLFolder.objects.get(id=client_post.data["id"])
        self.assertIsNotNone(objects_get)
        self.assertEqual(objects_get.id, client_post.data["id"])
        self.assertEqual(objects_get.name, client_post.data["name"])
        self.assertEqual(objects_get.parent, self.folder_root)

    def test_delete_folder(self):
        folder_to_be_delete = setup_folder(self.org, name="Folder to delete")

        client_delete = self.client.delete(
            f"/app/api/v1/folders/{folder_to_be_delete.id}"
        )

        self.assertEqual(client_delete.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(core.models.FTLFolder.DoesNotExist):
            FTLFolder.objects.get(id=folder_to_be_delete.id)

    def test_create_same_folder_name(self):
        # We try to create a folder with a name already used in setUp
        response = self.client.post(
            "/app/api/v1/folders", {"name": self.folder_root.name}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "folder_name_unique_for_org_level")

    def test_create_same_folder_name_at_same_level(self):
        # Specific test for an issue where a sub folder at the same level but not the same parent can be created
        # A
        # *  X
        # B
        # *  X

        folder_a = setup_folder(self.org, name="A")
        folder_a_x = setup_folder(self.org, name="X", parent=folder_a)
        folder_b = setup_folder(self.org, name="B")

        # A `X` folders can be created below `B`
        response = self.client.post(
            "/app/api/v1/folders", {"name": "X", "parent": folder_b.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # But not created below `A`
        response = self.client.post(
            "/app/api/v1/folders", {"name": "X", "parent": folder_a.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(celery.app, "send_task")
    def test_delete_folders_recursively(self, mock_send_task_delete_document):
        # A
        # *  B
        # *  B2
        #       * C

        folder_a = setup_folder(self.org, name="A")
        folder_a_b = setup_folder(self.org, name="B", parent=folder_a)
        folder_a_b2 = setup_folder(self.org, name="B2", parent=folder_a)
        folder_a_b2_c = setup_folder(self.org, name="B2", parent=folder_a_b2)

        doc_folder_a = setup_document(self.org, self.user, ftl_folder=folder_a)
        doc_folder_a_b2 = setup_document(self.org, self.user, ftl_folder=folder_a_b2)
        doc_folder_a_b2_c = setup_document(
            self.org, self.user, ftl_folder=folder_a_b2_c
        )

        response = self.client.delete(f"/app/api/v1/folders/{folder_a.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        doc_folder_a.refresh_from_db()
        doc_folder_a_b2.refresh_from_db()
        doc_folder_a_b2_c.refresh_from_db()

        self.assertTrue(doc_folder_a.deleted)
        self.assertTrue(doc_folder_a_b2.deleted)
        self.assertTrue(doc_folder_a_b2_c.deleted)


class JWTAuthenticationTests(APITestCase):
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

    def test_get_token(self):
        response = self.client.post(
            "/app/api/token",
            {"email": tv.USER1_EMAIL, "password": tv.USER1_PASS},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["access"])
        self.assertIsNotNone(response.data["refresh"])

    def test_refresh_token(self):
        response_token = self.client.post(
            "/app/api/token",
            {"email": tv.USER1_EMAIL, "password": tv.USER1_PASS},
            format="json",
        )

        response = self.client.post(
            "/app/api/token/refresh",
            {"refresh": response_token.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["access"])

    def test_use_token(self):
        response_token = self.client.post(
            "/app/api/token",
            {"email": tv.USER1_EMAIL, "password": tv.USER1_PASS},
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response_token.data["access"]}'
        )
        response = self.client.get("/app/api/v1/documents")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["count"])


@contextmanager
def execute_on_commit(immediately=False, using=None):
    """
    Context manager capturing transaction.on_commit() calls and executing
    them on exit or immediately if specified.

    This is required when using a subclass of django.test.TestCase as all
    tests are wrapped in a transaction that never gets committed.

    Django issue: https://code.djangoproject.com/ticket/30457
    """
    for_alias = DEFAULT_DB_ALIAS if using is None else using
    deferred = []

    def side_effect(func, using=None):
        alias = DEFAULT_DB_ALIAS if using is None else using
        if alias != for_alias:
            return
        if immediately:
            return func()
        deferred.append(func)

    with mock.patch("django.db.transaction.on_commit") as patch:
        patch.side_effect = side_effect
        yield patch
    for func in deferred:
        func()
