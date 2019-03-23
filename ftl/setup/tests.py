from django.test import TestCase

from ftests.tools.setup_helpers import setup_org


class SetupPagesTests(TestCase):

    def test_landing_page_step1_returns_correct_html(self):
        response = self.client.get('/setup/createorg/')
        self.assertContains(response, 'create first organization')
        self.assertTemplateUsed(response, 'setup/first_organization_creation_form.html')

    def test_landing_page_step2_returns_correct_html(self):
        response = self.client.get('/setup/createadmin/')
        self.assertContains(response, 'create the administrator')
        self.assertTemplateUsed(response, 'setup/admin_creation_form.html')

    def test_success_page_returns_correct_html(self):
        setup_org()

        response = self.client.get(f'/setup/success/')
        self.assertContains(response, 'Congratulations')
        self.assertTemplateUsed(response, 'setup/success.html')
