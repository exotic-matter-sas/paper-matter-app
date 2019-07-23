from ftests.pages.base_page import BasePage


class ResetPasswordPage(BasePage):
    url = '/password_reset/'

    page_title = 'h1'

    email_input = '#reset-password-form #id_email'
    submit_input = '#reset-password-form [type="submit"]'

    confirmation_message = ''

    def reset_password(self,  email):
        email_input = self.get_elem(self.email_input)
        submit_input = self.get_elem(self.submit_input)

        email_input.send_keys(email)
        submit_input.click()
