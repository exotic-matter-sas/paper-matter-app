import re

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

    def test_signup_to_first_org(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(user_num=1)

        # Success page appears
        self.assertIn('account was successfully created', self.get_elem(self.main_panel).text)

    def test_signup_to_second_org(self):
        # User create an account in the second org
        self.visit_signup_page(self.org_2.slug)
        self.create_user(user_num=2)

        # Success page appears
        self.assertIn('account was successfully created', self.get_elem(self.main_panel).text)

    def test_signup_failed(self):
        # User try to create an account without filling fields
        self.visit_signup_page(self.org_1.slug)
        self.get_elem(self.submit_input).click()

        # The browser refused form submission as all fields are set to required
        self.assertIn('signup', self.head_title)
        self.assertIn('Create your account', self.get_elem(self.page_title).text)

    def test_signup_receive_activation_email(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(user_num=1)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(tv.USER1_EMAIL, mail.outbox[0].to)
        self.assertIn('activate your account', mail.outbox[0].subject.lower())
        self.assertRegex(mail.outbox[0].body, 'https?://.+/accounts/activate/.+/')

    def test_signup_activate_account(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(user_num=1)

        self.assertEqual(len(mail.outbox), 1)
        activate_link = re.search(r'(https?://.+/accounts/activate/.+/)', mail.outbox[0].body)
        self.visit(activate_link.group(1), absolute_url=True)
        self.assertIn('Your email has been verified, thank you! You may go ahead and log in now.',
                      self.get_elem_text(self.main_panel))
