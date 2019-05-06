from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class AdminLoginPage(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = '/admin/'

        self.page_title = 'h2'

        self.admin_login_username_input = '#login-form #id_username'
        self.admin_login_password_input = '#login-form #id_password'
        self.admin_login_submit_input = '#login-form [type="submit"]'

        self.django_admin_success_message = '#user-tools'

    def log_admin(self):
        username_input = self.get_elem(self.admin_login_username_input)
        password_input = self.get_elem(self.admin_login_password_input)
        submit_input = self.get_elem(self.admin_login_submit_input)

        username_input.send_keys(tv.ADMIN_USERNAME)
        password_input.send_keys(tv.ADMIN_PASS)
        submit_input.click()
