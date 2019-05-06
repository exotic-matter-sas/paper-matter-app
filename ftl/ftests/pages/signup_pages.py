from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class SignupPages(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_title = 'h1'

        # Signup form
        self.username_input = '#user-form #id_username'
        self.email_address_input = '#user-form #id_email'
        self.password_input = '#user-form #id_password1'
        self.password_confirmation_input = '#user-form #id_password2'
        self.submit_input = '#user-form [type="submit"]'
        # Signup success
        self.user_login_link = '#user-login'

    def visit_signup_page(self, org_slug):
        self.visit(f'/signup/{org_slug}/')

    def create_user(self, user_num=1):
        username_input = self.get_elem(self.username_input)
        email_address_input = self.get_elem(self.email_address_input)
        password_input = self.get_elem(self.password_input)
        password_confirmation_input = self.get_elem(self.password_confirmation_input)
        submit_input = self.get_elem(self.submit_input)

        username = getattr(tv, f'USER{user_num}_USERNAME')
        username_input.send_keys(username)
        email_address_input.send_keys(getattr(tv, f'USER{user_num}_EMAIL'))
        password_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        password_confirmation_input.send_keys(getattr(tv, f'USER{user_num}_PASS'))
        submit_input.click()

        return username
