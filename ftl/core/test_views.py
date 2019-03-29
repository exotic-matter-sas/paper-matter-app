from django.test import TestCase

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
        self.assertContains(response, self.user.username)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_get_proper_context(self):
        """Home page get proper context"""
        response = self.client.get('/app/')
        self.assertEqual(response.context['org_name'], self.org.name)
        self.assertEqual(response.context['username'], self.user.username)

