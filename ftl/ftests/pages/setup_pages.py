from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class SetupPages(BasePage):
    create_org_url = '/setup/createorg/'
    create_admin_url = '/setup/create_admin/'
    setup_completed_url = '/setup/success/'

    page_title = 'h2'

    # Step 1/2
    org_name_input = '#organization-form #id_name'
    org_slug_input = '#organization-form #id_slug'
    org_submit_input = '#organization-form [type="submit"]'
    # Step 2/2
    admin_username_input = '#admin-form #id_username'
    admin_email_address_input = '#admin-form #id_email'
    admin_password_input = '#admin-form #id_password1'
    admin_password_confirmation_input = '#admin-form #id_password2'
    admin_submit_input = '#admin-form [type="submit"]'
    # Setup completed
    admin_login_link = '#admin-login'
    user_signup_link = '#user-signup'

    def create_first_organization(self):
        name_input = self.get_elem(self.org_name_input)
        slug_input = self.get_elem(self.org_slug_input)
        submit_input = self.get_elem(self.org_submit_input)

        name_input.send_keys(tv.ORG_NAME)
        slug_input.send_keys(tv.ORG_SLUG)
        submit_input.click()

    def create_admin(self):
        username_input = self.get_elem(self.admin_username_input)
        email_address_input = self.get_elem(self.admin_email_address_input)
        password_input = self.get_elem(self.admin_password_input)
        password_confirmation_input = self.get_elem(self.admin_password_confirmation_input)
        submit_input = self.get_elem(self.admin_submit_input)

        username_input.send_keys(tv.ADMIN_USERNAME)
        email_address_input.send_keys(tv.ADMIN_EMAIL)
        password_input.send_keys(tv.ADMIN_PASS)
        password_confirmation_input.send_keys(tv.ADMIN_PASS)
        submit_input.click()
