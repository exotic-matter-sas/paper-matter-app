from unittest import skip

from django.test import TestCase


class SetupPageTest(TestCase):

    def test_landing_page_step1_returns_correct_html(self):
        response = self.client.get('/setup/1/')
        self.assertContains(response, 'Admin creation')
        self.assertTemplateUsed(response, 'setup/admin_creation_form.html')

    def test_landing_page_step2_returns_correct_html(self):
        response = self.client.get('/setup/2/')
        self.assertContains(response, 'First organization creation')
        self.assertTemplateUsed(response, 'setup/first_organization_creation_form.html')

    @skip
    def test_success_page_returns_correct_html(self):
        # TODO create organization before testing this page (make a decorator ?)
        response = self.client.get('/setup/success/')
        self.assertContains(response, 'Congratulations')
        self.assertTemplateUsed(response, 'setup/success.html')
