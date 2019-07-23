from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse_lazy
from tika import parser

from core.views import _extract_text_from_pdf
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_authenticated_session, setup_document


class CorePagesTests(TestCase):

    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)

    def test_home_returns_correct_html(self):
        response = self.client.get('/app/')
        self.assertContains(
            response,
            f'<script id="ftlAccount" type="application/json">{{"name": "{self.user.username}"}}</script>')
        self.assertContains(response, '<div id="app">')
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_get_proper_context(self):
        response = self.client.get('/app/')
        self.assertEqual(response.context['org_name'], self.org.name)
        self.assertEqual(response.context['ftl_account'], {'name': self.user.username})


class DownloadDocumentTests(TestCase):
    def setUp(self):
        # Setup org, admin, user and log the user
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)

    def test_document_download_returns_proper_binary(self):
        # Add a document and log user
        doc = setup_document(self.org, self.user)
        setup_authenticated_session(self.client, self.org, self.user)

        response = self.client.get(f'/app/uploads/{doc.pid}')

        with open(doc.binary.path, 'rb') as uploaded_doc:
            self.assertEqual(uploaded_doc.read(), response.content)

    def test_document_download_doesnt_work_if_not_logged(self):
        # Add a document in first org with first user
        doc = setup_document(self.org, self.user)

        # Trying to download the document when not logged redirect to login page
        download_url = f'/app/uploads/{doc.pid}'
        response = self.client.get(download_url)
        self.assertRedirects(response, f'{reverse_lazy("login")}?next={quote_plus(download_url)}')

    def test_document_download_only_work_for_users_in_the_doc_org(self):
        # Add a document in first org with first user
        doc = setup_document(self.org, self.user)

        # Create a second org and user, log the second user
        org_2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)
        user_2 = setup_user(org_2, tv.USER2_EMAIL, tv.USER2_USERNAME, tv.USER2_PASS)
        setup_authenticated_session(self.client, org_2, user_2)

        # Trying to download the document of first org with a user of second org returns a 404
        response = self.client.get(f'/app/uploads/{doc.pid}')
        self.assertEqual(response.status_code, 404)


class PDFViewerTests(TestCase):
    def test_pdf_viewer_accessible(self):
        result = finders.find('pdfjs/web/viewer.html')
        self.assertIsNotNone(result, 'Pdfjs resources not found')


class IndexerTests(TestCase):
    @patch.object(parser, 'from_file')
    def test_text_extraction(self, mock_parser):
        indexed_text_ = {"content": "indexed text"}
        mock_parser.return_value = indexed_text_

        vector = MagicMock()
        ftl_doc = MagicMock()

        _extract_text_from_pdf(vector, ftl_doc)

        mock_parser.assert_called_once_with(ftl_doc.binary.name)
        self.assertEqual(ftl_doc.content_text, indexed_text_['content'])
        self.assertEqual(ftl_doc.tsvector, vector)
