from django.test import TestCase
from django.urls import reverse_lazy

from ftests.tools.setup_helpers import setup_org, setup_admin
from ftests.tools import test_values as tv
from .forms import FTLUserCreationForm


class FtlPagesTests(TestCase):

    def test_index_redirects(self):
        """Index redirect to correct page according to setup state"""
        response = self.client.get('')
        self.assertRedirects(response, reverse_lazy('setup:create_org'))

        org = setup_org()
        response = self.client.get('')
        self.assertRedirects(response, reverse_lazy('setup:create_admin'))

        setup_admin(org)
        response = self.client.get('')
        self.assertRedirects(response, reverse_lazy('login'))

    def test_signup_returns_correct_html(self):
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/')
        self.assertContains(response, 'Create your account')
        self.assertTemplateUsed(response, 'ftl/signup.html')

    def test_signup_context(self):
        """Signup page get proper context"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/')
        self.assertEqual(response.context['org_name'], org.name)
        self.assertIsInstance(response.context['form'], FTLUserCreationForm)

    def test_signup_get_success_url(self):
        """Signup get_success_url working properly"""
        org = setup_org()

        response = self.client.post(f'/signup/{org.slug}/',
                                    {
                                        'username': tv.USER1_USERNAME,
                                        'email': tv.USER1_EMAIL,
                                        'password1': tv.USER1_PASS,
                                        'password2': tv.USER1_PASS,
                                    })

        self.assertRedirects(response, reverse_lazy('signup_success', kwargs={'org_slug': org.slug}))

    def test_signup_success_returns_correct_html(self):
        """Signup success page returns correct html"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/success/')
        self.assertContains(response, 'Congratulations')
        self.assertTemplateUsed(response, 'ftl/signup_success.html')

    def test_signup_success_get_proper_context(self):
        """Signup success page get proper context"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/success/')
        self.assertEqual(response.context['org_slug'], org.slug)
