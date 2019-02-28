from django.test import TestCase


class SetupPageTest(TestCase):

    def test_landing_page_returns_correct_html(self):
        response = self.client.get('/setup/')
        self.assertContains(response, 'Landing page')
        self.assertTemplateUsed(response, 'setup/admin_and_first_organization_creation_form.html')
