from django.test import TestCase
from django.http import HttpRequest

from ftests.tools.setup_helpers import setup_org
from .views import CreateOrg, CreateAdmin


class SetupPagesTests(TestCase):

    def test_create_first_org_page_returns_correct_html(self):
        """create_first_org page return correct html"""
        response = self.client.get('/setup/createorg/')
        self.assertContains(response, 'create first organization')
        self.assertTemplateUsed(response, 'setup/first_organization_creation_form.html')

    def test_create_first_org_page_redirect_to_create_admin_after_first_org_creation(self):
        """create_first_org page redirect to create_admin page once first org created"""
        pass  # TODO

    def test_create_first_org_page_get_proper_context(self):
        """create_first_org page get proper context"""
        response = self.client.get('/setup/createorg/')
        request = HttpRequest()

        self.assertEqual(response.context['form'].as_p(), CreateOrg(request=request).get_form().as_p())

    def test_create_admin_page_returns_correct_html(self):
        """create_admin page return correct html"""
        response = self.client.get('/setup/createadmin/')
        self.assertContains(response, 'create the administrator')
        self.assertTemplateUsed(response, 'setup/admin_creation_form.html')

    def test_create_admin_page_redirect_to_success_after_admin_creation(self):
        """create_admin page redirect to success page once admin created"""
        pass  # TODO

    def test_create_admin_page_get_proper_context(self):
        """create-admin page get proper context"""
        """create_first_org page get proper context"""
        response = self.client.get('/setup/createadmin/')

        self.assertIsInstance(response.context['form'], CreateAdmin.form_class)

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
