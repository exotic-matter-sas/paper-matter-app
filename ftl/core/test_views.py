#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import datetime
import time
import uuid
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse_lazy

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
    setup_document,
    setup_document_share,
)
from ftl.enums import FTLStorages


class CorePagesTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org, tz="UTC")
        setup_authenticated_session(self.client, self.org, self.user)

    def test_home_returns_correct_html(self):
        response = self.client.get("/app/")
        self.assertContains(
            response, f'<script id="ftlAccount" type="application/json">'
        )
        self.assertContains(response, f'"name": "{self.user.email}"')
        self.assertContains(response, f'"isSuperUser": false')
        self.assertContains(response, '<div id="app">')
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_get_proper_context(self):
        response = self.client.get("/app/")
        # Use comparaison operator to do a subset test
        self.assertLessEqual(
            {
                "name": self.user.email,
                "isSuperUser": False,
                "otp_warning": False,
                "supported_exts": {
                    "application/pdf": ".pdf",
                    "text/plain": ".txt",
                    "application/rtf": ".rtf",
                    "text/rtf": ".rtf",
                    "application/msword": ".doc",
                    "application/vnd.ms-excel": ".xls",
                    "application/excel": ".xls",
                    "application/vnd.ms-powerpoint": ".ppt",
                    "application/mspowerpoint": ".ppt",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
                    "application/vnd.oasis.opendocument.text": ".odt",
                    "application/vnd.oasis.opendocument.presentation": ".odp",
                    "application/vnd.oasis.opendocument.spreadsheet": ".ods",
                },
                "only_office_viewer": False,
                "tz_offset": 0.0,
            }.items(),
            response.context["ftl_account"].items(),
        )


class DownloadDocumentTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

    @override_settings(DEFAULT_FILE_STORAGE=FTLStorages.FILE_SYSTEM)
    def test_document_download_returns_proper_binary(self):
        # Add a document and log user
        doc = setup_document(self.org, self.user)
        setup_authenticated_session(self.client, self.org, self.user)

        response = self.client.get(f"/app/api/v1/documents/{doc.pid}/download")

        with open(doc.binary.path, "rb") as uploaded_doc:
            self.assertEqual(uploaded_doc.read(), response.content)

    def test_document_download_doesnt_work_if_not_logged(self):
        # Add a document in first org with first user
        doc = setup_document(self.org, self.user)

        # Trying to download the document when not logged returns an error
        download_url = f"/app/api/v1/documents/{doc.pid}/download"
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 403)

    def test_document_download_only_work_for_users_in_the_doc_org(self):
        # Add a document in first org with first user
        doc = setup_document(self.org, self.user)

        # Create a second org and user, log the second user
        org_2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)
        user_2 = setup_user(org_2, tv.USER2_EMAIL, tv.USER2_PASS)
        setup_authenticated_session(self.client, org_2, user_2)

        # Trying to download the document of first org with a user of second org returns a 404
        response = self.client.get(f"/app/api/v1/documents/{doc.pid}/download")
        self.assertEqual(response.status_code, 404)

    @override_settings(FTL_ENABLE_ONLY_OFFICE=True)
    @override_settings(FTL_ONLY_OFFICE_PUBLIC_JS_URL="http://example.org/oo.js")
    @override_settings(FTL_ONLY_OFFICE_API_SERVER_URL="http://example-api.org")
    @override_settings(
        FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL="http://example-download.org"
    )
    @override_settings(FTL_ONLY_OFFICE_SECRET_KEY="test_secret")
    def test_temp_document_download(self):
        doc = setup_document(
            self.org,
            self.user,
            title=tv.DOCUMENT_DOCX_TITLE,
            note=tv.DOCUMENT_DOCX_NOTE,
            text_content=tv.DOCUMENT_DOCX_CONTENT,
            binary=tv.DOCUMENT_DOCX_BINARY_PATH,
            type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        setup_authenticated_session(self.client, self.org, self.user)

        response = self.client.get(f"/app/api/v1/documents/{doc.pid}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("only_office_config", response.data)
        self.assertIn("document", response.data["only_office_config"])
        self.assertIn("url", response.data["only_office_config"]["document"])

        response = self.client.get(
            response.data["only_office_config"]["document"]["url"]
        )

        with open(doc.binary.path, "rb") as uploaded_doc:
            self.assertEqual(uploaded_doc.read(), response.content)

    @override_settings(FTL_ENABLE_ONLY_OFFICE=True)
    @override_settings(FTL_ONLY_OFFICE_PUBLIC_JS_URL="http://example.org/oo.js")
    @override_settings(FTL_ONLY_OFFICE_API_SERVER_URL="http://example-api.org")
    @override_settings(
        FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL="http://example-download.org"
    )
    @override_settings(FTL_ONLY_OFFICE_SECRET_KEY="test_secret")
    @patch.object(time, "time")
    def test_temp_document_download_expired(self, mocked_time):
        mocked_time.return_value = time.mktime(
            datetime.datetime(2019, 1, 1).timetuple()
        )

        doc = setup_document(self.org, self.user)
        setup_authenticated_session(self.client, self.org, self.user)

        response = self.client.get(
            reverse_lazy("api_temp_download_url", kwargs={"spid": doc.pid}), follow=True
        )

        self.assertEqual(response.status_code, 404)


class PDFViewerTests(TestCase):
    def test_pdf_viewer_accessible(self):
        result = finders.find("pdfjs/web/viewer.html")
        self.assertIsNotNone(result, "Pdfjs resources not found")


class DocumentSharingTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

    def test_view_shared_document(self):
        doc = setup_document(self.org, self.user)
        doc_share = setup_document_share(doc)

        response = self.client.get(f"/app/share/{doc_share.pid}")
        self.assertEqual(response.status_code, 200)

    def test_cant_use_doc_pid_for_sharing(self):
        doc = setup_document(self.org, self.user)

        response = self.client.get(f"/app/share/{doc.pid}")
        self.assertEqual(response.status_code, 404)

    def test_download_shared_document(self):
        doc = setup_document(self.org, self.user)
        doc_share = setup_document_share(doc)

        response = self.client.get(f"/app/share/{doc_share.pid}/download")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/octet-stream")

    def test_cant_view_unshared_document(self):
        doc = setup_document(self.org, self.user)
        doc_share = setup_document_share(doc)

        response = self.client.get(f"/app/share/{doc_share.pid}")
        self.assertEqual(response.status_code, 200)

        doc_share.delete()

        response = self.client.get(f"/app/share/{doc_share.pid}")
        self.assertEqual(response.status_code, 404)

    def test_custom_404_share_document(self):
        response = self.client.get(f"/app/share/{uuid.uuid4()}")
        self.assertContains(response, "document was not found", status_code=404)

    def test_cant_view_expired_shared_document(self):
        doc = setup_document(self.org, self.user)
        doc_share = setup_document_share(
            doc, expire_at=datetime.datetime.now() - datetime.timedelta(hours=1)
        )

        response = self.client.get(f"/app/share/{doc_share.pid}")
        self.assertEqual(response.status_code, 404)

    @override_settings(FTL_ENABLE_ONLY_OFFICE=True)
    @override_settings(FTL_ONLY_OFFICE_PUBLIC_JS_URL="http://example.org/oo.js")
    @override_settings(FTL_ONLY_OFFICE_API_SERVER_URL="http://example-api.org")
    @override_settings(
        FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL="http://example-download.org"
    )
    @override_settings(FTL_ONLY_OFFICE_SECRET_KEY="test_secret")
    def test_only_office_viewer(self):
        doc = setup_document(
            self.org,
            self.user,
            title=tv.DOCUMENT_DOCX_TITLE,
            note=tv.DOCUMENT_DOCX_NOTE,
            text_content=tv.DOCUMENT_DOCX_CONTENT,
            binary=tv.DOCUMENT_DOCX_BINARY_PATH,
            type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        doc_share = setup_document_share(doc)

        response = self.client.get(f"/app/share/{doc_share.pid}")

        self.assertContains(response, "onlyoffice-embed-container", status_code=200)

        self.assertIn("only_office_supported_ext", response.context)
        self.assertIn("only_office_config", response.context)

        self.assertIn("document", response.context["only_office_config"])
        self.assertIn("editorConfig", response.context["only_office_config"])
        self.assertIn("token", response.context["only_office_config"])

        self.assertIn("url", response.context["only_office_config"]["document"])
        self.assertIn("fileType", response.context["only_office_config"]["document"])
        self.assertIn("key", response.context["only_office_config"]["document"])
        self.assertIn("title", response.context["only_office_config"]["document"])
        self.assertIn("permissions", response.context["only_office_config"]["document"])
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
            response.context["only_office_config"]["document"]["permissions"],
        )

        self.assertIn("lang", response.context["only_office_config"]["editorConfig"])
        self.assertIn("mode", response.context["only_office_config"]["editorConfig"])
        self.assertIn(
            "customization", response.context["only_office_config"]["editorConfig"]
        )
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
            response.context["only_office_config"]["editorConfig"]["customization"],
        )
