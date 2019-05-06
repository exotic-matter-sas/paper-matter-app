from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class LoginPage(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = '/login/'

        self.page_title = 'h1'

        self.login_username_input = '#login-form #id_username'
        self.login_password_input = '#login-form #id_password'
        self.login_submit_input = '#login-form [type="submit"]'

        self.login_success_div = '#app'

    def log_user(self,  user_num=1):
        username_input = self.get_elem(self.login_username_input)
        password_input = self.get_elem(self.login_password_input)
        submit_input = self.get_elem(self.login_submit_input)

        username_input.send_keys(getattr(tv, f'USER{user_num}_USERNAME'))
        password_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        submit_input.click()
