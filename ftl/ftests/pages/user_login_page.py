from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class LoginPage(BasePage):
    url = '/login/'

    page_title = 'h1'

    login_email_input = '#login-form #id_email'
    login_password_input = '#login-form #id_password'
    login_submit_input = '#login-form [type="submit"]'

    login_success_div = '#app'
    login_failed_div = '#login-form .errorlist'
    login_messages = '#messages'

    password_reset_link = '#password-reset'

    def log_user(self,  user_num=1, email=None, password=None):
        email_input = self.get_elem(self.login_email_input)
        password_input = self.get_elem(self.login_password_input)
        submit_input = self.get_elem(self.login_submit_input)

        if not email:
            email = getattr(tv, f'USER{user_num}_EMAIL')
        if not password:
            password = getattr(tv, f'USER{user_num}_PASS')

        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_input.click()
