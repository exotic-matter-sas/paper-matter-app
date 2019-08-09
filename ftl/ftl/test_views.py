from unittest.mock import patch, Mock

from django.contrib import messages
from django.test import TestCase
from django.urls import reverse_lazy
from django.contrib.auth.signals import user_logged_out

from core.models import FTLUser, FTL_PERMISSIONS_USER
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_authenticated_session
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

    @patch.object(user_logged_out, 'send')
    def test_logout_call_proper_signal(self, mocked_signal):
        # Setup org, admin, user and log the user
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        setup_authenticated_session(self.client, org, user)

        self.client.get('/logout/')

        mocked_signal.assert_called_once()

    @patch.object(messages, 'success')
    def test_logout_signal_trigger_django_messages(self, messages_mocked):
        message_to_display_on_login_page = 'bingo!'
        messages_mocked.return_value = message_to_display_on_login_page
        mocked_request = Mock()
        mocked_request.GET = {}
        user_logged_out.send(self.__class__, request=mocked_request)

        messages_mocked.assert_called_once()
