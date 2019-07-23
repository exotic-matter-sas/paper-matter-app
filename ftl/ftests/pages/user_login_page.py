from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class LoginPage(BasePage):
    url = '/login/'

    page_title = 'h1'

    login_username_input = '#login-form #id_username'
    login_password_input = '#login-form #id_password'
    login_submit_input = '#login-form [type="submit"]'

    login_success_div = '#app'
    login_failed_div = '#login-form .errorlist'

    password_reset_link = '#password-reset'

    def log_user(self,  user_num=1, username=None, password=None):
        username_input = self.get_elem(self.login_username_input)
        password_input = self.get_elem(self.login_password_input)
        submit_input = self.get_elem(self.login_submit_input)

        if not username:
            username = getattr(tv, f'USER{user_num}_USERNAME')
        if not password:
            password = getattr(tv, f'USER{user_num}_PASS')

        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_input.click()
