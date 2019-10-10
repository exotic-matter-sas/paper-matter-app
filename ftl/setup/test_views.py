from django.test import TestCase
from django.urls import reverse_lazy

from ftests.tools.setup_helpers import setup_org, setup_admin
from .views import CreateFirstOrgAndAdmin


class SetupPagesTests(TestCase):

    def test_create_admin_page_returns_correct_html(self):
        """create_admin page return correct html"""
        setup_org()

        response = self.client.get('/setup/createadmin/')
        self.assertContains(response, 'Create administrator')
        self.assertTemplateUsed(response, 'setup/first_org_and_admin_creation_form.html')

    def test_create_admin_page_redirect_to_success_after_admin_creation(self):
        """create_admin page redirect to success page once admin created"""
        setup_admin(setup_org())

        response = self.client.get(reverse_lazy('setup:create_admin'))
        self.assertRedirects(response, reverse_lazy('login'))

    def test_create_admin_page_get_proper_context(self):
        """create-admin page get proper context"""
        setup_org()

        response = self.client.get('/setup/createadmin/')
        self.assertIsInstance(response.context['form'], CreateFirstOrgAndAdmin.form_class)

    def test_success_page_returns_correct_html(self):
        """success page return correct html"""
        setup_org()

        response = self.client.get(f'/setup/success/')
        self.assertContains(response, 'Congratulations')
        self.assertTemplateUsed(response, 'setup/success.html')

    def test_success_page_get_proper_context(self):
        """success page get proper context"""
        org = setup_org()

        response = self.client.get(f'/setup/success/')
        expected_context = {
            'org_slug': org.slug,
            'org_name': org.name,
        }
        self.assertEqual(response.context['org_slug'], expected_context['org_slug'])
        self.assertEqual(response.context['org_name'], expected_context['org_name'])
