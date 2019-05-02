from django.test import TestCase
from django.contrib.staticfiles import finders

from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_authenticated_session


class CorePagesTests(TestCase):

    def setUp(self):
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)

    def test_home_page_returns_correct_html(self):
        """Home page returns correct html"""
        response = self.client.get('/app/')
        self.assertContains(
            response,
            f'<script id="ftlAccount" type="application/json">{{"name": "{self.user.username}"}}</script>')
        self.assertContains(response, '<div id="app"></div>')
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_get_proper_context(self):
        """Home page get proper context"""
        response = self.client.get('/app/')
        self.assertEqual(response.context['org_name'], self.org.name)
        self.assertEqual(response.context['ftl_account'], {'name': self.user.username})


class PDFViewerTests(TestCase):
    def test_pdf_viewer_accessible(self):
        """Test pdfj view resource are present"""
        result = finders.find('pdfjs/web/viewer.html')
        self.assertIsNotNone(result, 'Pdfjs resources not found')
