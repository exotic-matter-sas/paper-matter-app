from django.test import TestCase
from django.urls import reverse_lazy

from core.models import FTLUser, FTL_PERMISSIONS_USER
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin
from .forms import FTLUserCreationForm


class FtlPagesTests(TestCase):

    def test_index_redirects(self):
        """Index redirect to correct page according to setup state"""
        response = self.client.get('', follow=True)
        self.assertRedirects(response, reverse_lazy('setup:create_first_org'))

        org = setup_org()
        response = self.client.get('', follow=True)
        self.assertRedirects(response, reverse_lazy('setup:create_admin'))

        setup_admin(org)
        response = self.client.get('', follow=True)
        self.assertRedirects(response, f"{reverse_lazy('login')}?next={reverse_lazy('home')}")

    def test_signup_returns_correct_html(self):
        """Signup page returns correct html"""
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
        self.assertContains(response, 'verify your email')
        self.assertTemplateUsed(response, 'ftl/signup_success.html')

    def test_signup_success_get_proper_context(self):
        """Signup success page get proper context"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/success/')
        self.assertEqual(response.context['org_slug'], org.slug)

    def test_user_permissions_signup(self):
        org = setup_org()

        self.client.post(f'/signup/{org.slug}/',
                         {
                             'username': tv.USER1_USERNAME,
                             'email': tv.USER1_EMAIL,
                             'password1': tv.USER1_PASS,
                             'password2': tv.USER1_PASS,
                         })

        user = FTLUser.objects.get(username=tv.USER1_USERNAME)
        self.assertIsNotNone(user)
        self.assertTrue(user.has_perms(FTL_PERMISSIONS_USER))
