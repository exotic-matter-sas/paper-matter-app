import re
from unittest import skip

from django.core import mail

from ftests.pages.signup_pages import SignupPages
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin


class SignupPageTests(SignupPages):
    def setUp(self, **kwargs):
        # first org and admin already created
        super().setUp()
        self.org_1 = setup_org(tv.ORG_NAME_1, tv.ORG_SLUG_1)
        setup_admin(org=self.org_1)
        self.org_2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)

    @skip("Multi users feature disabled")
    def test_signup_to_first_org(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(user_num=1)

        # Success page appears
        self.assertIn('verify your email to activate your account', self.get_elem(self.main_panel).text)

    @skip("Multi users feature disabled")
    def test_signup_to_second_org(self):
        # User create an account in the second org
        self.visit_signup_page(self.org_2.slug)
        self.create_user(user_num=2)

        # Success page appears
        self.assertIn('verify your email to activate your account', self.get_elem(self.main_panel).text)

    @skip("Multi users feature disabled")
    def test_signup_failed(self):
        # User try to create an account without filling fields
        self.visit_signup_page(self.org_1.slug)
        self.get_elem(self.submit_input).click()

        # The browser refused form submission as all fields are set to required
        self.assertIn('signup', self.head_title)
        self.assertIn('Create your account', self.get_elem(self.page_title).text)

    @skip("Multi users feature disabled")
    def test_signup_receive_activation_email(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(tv.USER1_EMAIL, mail.outbox[0].to)
        self.assertIn('activate your account', mail.outbox[0].subject.lower())
        self.assertRegex(mail.outbox[0].body, 'https?://.+/accounts/activate/.+/')

    @skip("Multi users feature disabled")
    def test_signup_activate_account(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(activate_user=True)

        self.assertIn('Your email has been verified, thank you! You may go ahead and log in now.',
                      self.get_elem_text(self.main_panel))

    @skip("Multi users feature disabled")
    def test_signup_activate_account_failed(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user()

        # User use a bad activation link
        bad_activation_link = '/accounts/activate/B4dT0k3n/'

        self.visit(bad_activation_link)
        self.assertIn('could not activate the account',
                      self.get_elem_text(self.main_panel))
