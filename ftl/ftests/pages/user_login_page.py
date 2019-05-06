from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class LoginPage(BasePage):
    url = '/login/'

    page_title = 'h1'

    login_username_input = '#login-form #id_username'
    login_password_input = '#login-form #id_password'
    login_submit_input = '#login-form [type="submit"]'

    login_success_div = '#app'

    def log_user(self,  user_num=1):
        username_input = self.get_elem(self.login_username_input)
        password_input = self.get_elem(self.login_password_input)
        submit_input = self.get_elem(self.login_submit_input)

        username_input.send_keys(getattr(tv, f'USER{user_num}_USERNAME'))
        password_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        submit_input.click()
