#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django.http import HttpRequest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import FTLDocument
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_folder,
)


class DocumentDetailsOnlyOfficeDisableTests(APITestCase):
    # Given default settings
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(
            self.org,
            self.user,
            title=tv.DOCUMENT_DOCX_TITLE,
            note=tv.DOCUMENT_DOCX_NOTE,
            text_content=tv.DOCUMENT_DOCX_CONTENT,
            binary=tv.DOCUMENT_DOCX_BINARY_PATH,
            type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

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

    def test_get_doc_has_not_only_office_config(self):
        # Document detail API doesn't return
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        client_get = self.client.get(
            f"/app/api/v1/documents/{str(self.doc.pid)}", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc = client_get.data
        self.assertNotIn("only_office_config", client_doc)


@override_settings(FTL_ENABLE_ONLY_OFFICE=True)
@override_settings(FTL_ONLY_OFFICE_PUBLIC_JS_URL="http://example.org/oo.js")
@override_settings(FTL_ONLY_OFFICE_API_SERVER_URL="http://example-api.org")
@override_settings(
    FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL="http://example-download.org"
)
@override_settings(FTL_ONLY_OFFICE_SECRET_KEY="test_secret")
class DocumentDetailsOnlyOfficeTests(APITestCase):
    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

        self.doc = setup_document(
            self.org,
            self.user,
            title=tv.DOCUMENT_DOCX_TITLE,
            note=tv.DOCUMENT_DOCX_NOTE,
            text_content=tv.DOCUMENT_DOCX_CONTENT,
            binary=tv.DOCUMENT_DOCX_BINARY_PATH,
            type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

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

    def test_get_doc_has_only_office_config(self):
        # Document detail API must return a signed only office configuration json
        ftl_document_first = FTLDocument.objects.get(pid=self.doc.pid)
        self.assertIsNotNone(ftl_document_first.pid)

        client_get = self.client.get(
            f"/app/api/v1/documents/{str(self.doc.pid)}", format="json"
        )
        self.assertEqual(client_get.status_code, status.HTTP_200_OK)

        client_doc = client_get.data
        self.assertIn("only_office_config", client_doc)
        self.assertIn("document", client_doc["only_office_config"])
        self.assertIn("editorConfig", client_doc["only_office_config"])
        self.assertIn("token", client_doc["only_office_config"])

        self.assertIn("url", client_doc["only_office_config"]["document"])
        self.assertIn("fileType", client_doc["only_office_config"]["document"])
        self.assertIn("key", client_doc["only_office_config"]["document"])
        self.assertIn("title", client_doc["only_office_config"]["document"])
        self.assertIn("permissions", client_doc["only_office_config"]["document"])
        self.assertDictEqual(
            {
                "comment": False,
                "copy": True,
                "download": True,
                "edit": False,
                "fillForms": False,
                "modifyContentControl": False,
                "modifyFilter": False,
                "print": True,
                "review": False,
            },
            client_doc["only_office_config"]["document"]["permissions"],
        )

        self.assertIn("lang", client_doc["only_office_config"]["editorConfig"])
        self.assertIn("mode", client_doc["only_office_config"]["editorConfig"])
        self.assertIn("customization", client_doc["only_office_config"]["editorConfig"])
        self.assertDictEqual(
            {
                "autosave": False,
                "chat": False,
                "commentAuthorOnly": False,
                "comments": False,
                "compactHeader": False,
                "compactToolbar": False,
                "compatibleFeatures": False,
                "help": True,
                "hideRightMenu": False,
                "mentionShare": False,
                "plugins": False,
                "reviewDisplay": "original",
                "showReviewChanges": False,
                "spellcheck": False,
                "toolbarNoTabs": False,
                "unit": "cm",
                "zoom": -2,
            },
            client_doc["only_office_config"]["editorConfig"]["customization"],
        )
