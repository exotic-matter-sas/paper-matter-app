from django.test import TestCase

from ftests.tools.setup_helpers import setup_org
from ftests.tools import test_values as tv


class SetupPagesTests(TestCase):

    def test_landing_page_step1_returns_correct_html(self):
        response = self.client.get('/setup/1/')
        self.assertContains(response, 'Admin creation')
        self.assertTemplateUsed(response, 'setup/admin_creation_form.html')

    def test_landing_page_step2_returns_correct_html(self):
        response = self.client.get('/setup/2/')
        self.assertContains(response, 'First organization creation')
        self.assertTemplateUsed(response, 'setup/first_organization_creation_form.html')

    def test_success_page_returns_correct_html(self):
        setup_org()

        response = self.client.get(f'/setup/{tv.ORG_SLUG}/success/')
        self.assertContains(response, 'Congratulations')
        self.assertTemplateUsed(response, 'setup/success.html')
