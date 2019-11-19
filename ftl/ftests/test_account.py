from unittest import skipIf

from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import DEV_MODE


class AccountPageTests(LoginPage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_change_password(self):
        # Go to account management / password change
        self.visit("/accounts/password")

        # Enter form data
        old_pass_input = self.get_elem("#id_old_password")
        new_pass1_input = self.get_elem("#id_new_password1")
        new_pass2_input = self.get_elem("#id_new_password2")
        submit_input = self.get_elem("form [type=submit]")

        old_pass_input.send_keys(tv.USER1_PASS)
        new_pass1_input.send_keys("new password")
        new_pass2_input.send_keys("new password")
        submit_input.click()

        self.assertIn('Password updated!', self.get_elem_text("div.text-center"))

        # Logout
        self.visit("/logout")

        # Ensure can't log with old password
        self.visit(LoginPage.url)
        self.log_user()
        self.assertIn('email address and password', self.get_elem_text(self.login_failed_div),
                      'User login should failed using its old password')

        # User is able to login using its new password
        self.log_user(password="new_password")
        self.assertIsNotNone(self.login_success_div,
                             'User login should success using new password')
