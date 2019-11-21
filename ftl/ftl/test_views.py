import re
from unittest import skip
from unittest.mock import patch, Mock

from django.contrib import messages
from django.contrib.auth.signals import user_logged_out
from django.core import mail
from django.test import TestCase
from django.urls import reverse_lazy

from core.models import FTLUser, FTL_PERMISSIONS_USER
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_authenticated_session
from .forms import FTLUserCreationForm


class FtlPagesTests(TestCase):

    def test_index_redirects(self):
        """Index redirect to correct page according to setup state"""
        response = self.client.get('', follow=True)
        self.assertRedirects(response, reverse_lazy('setup:create_admin'))

        org = setup_org()
        setup_admin(org)
        response = self.client.get('', follow=True)
        self.assertRedirects(response, f"{reverse_lazy('login')}?next={reverse_lazy('home')}")

    @skip("Multi users feature disabled")
    def test_signup_returns_correct_html(self):
        """Signup page returns correct html"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/')
        self.assertContains(response, 'Create your account')
        self.assertTemplateUsed(response, 'ftl/registration/signup.html')

    @skip("Multi users feature disabled")
    def test_signup_context(self):
        """Signup page get proper context"""
        org = setup_org()

        response = self.client.get(f'/signup/{org.slug}/')
        self.assertEqual(response.context['org_name'], org.name)
        self.assertIsInstance(response.context['form'], FTLUserCreationForm)

    @skip("Multi users feature disabled")
    def test_signup_get_success_url(self):
        """Signup get_success_url working properly"""
        org = setup_org()

        response = self.client.post(f'/signup/{org.slug}/',
                                    {
                                        'email': tv.USER1_EMAIL,
                                        'password1': tv.USER1_PASS,
                                        'password2': tv.USER1_PASS,
                                    })

        self.assertRedirects(response, reverse_lazy('signup_success'), fetch_redirect_response=False)

    def test_signup_success_returns_correct_html(self):
        """Signup success page returns correct html"""

        response = self.client.get(f'/signup/success/')
        self.assertContains(response, 'verify your email')
        self.assertTemplateUsed(response, 'ftl/registration/signup_success.html')

    @skip("Multi users feature disabled")
    def test_user_permissions_signup(self):
        org = setup_org()

        self.client.post(f'/signup/{org.slug}/',
                         {
                             'email': tv.USER1_EMAIL,
                             'password1': tv.USER1_PASS,
                             'password2': tv.USER1_PASS,
                         })

        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        self.assertIsNotNone(user)

        # To test permission, we need an account activated otherwise the permissions are not set
        self.assertEqual(len(mail.outbox), 1)
        activate_link = re.search(r'(https?://.+/accounts/activate/.+/)', mail.outbox[0].body)
        response = self.client.get(activate_link.group(1), follow=True)
        self.assertEqual(response.status_code, 200)
        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
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
