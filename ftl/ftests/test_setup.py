from ftests.pages.django_admin_login_page import AdminLoginPage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.signup_pages import SignupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_admin, setup_org, setup_user


class LandingPageTests(SetupPages):
    def test_index_redirect_to_first_admin_creation_on_first_visit(self):
        """Index page redirect to first organization creation page on first visit"""
        # Admin user have just install app and display it for the first time
        self.visit(self.root_url)

        # The user is welcomed and asked to complete 1st setup step: org creation
        self.assertIn(tv.APP_NAME.lower(), self.head_title)
        self.assertIn('create administrator', self.head_title)

    def test_landing_page_redirect_to_user_login_when_setup_complete(self):
        """Landing page redirect to user login page when setup complete"""
        self.visit(self.root_url)

        # He fulfill the admin creation form
        self.create_admin()

        # A success page appears mentioning the urls for admin login page and user signup page
        self.assertIn('setup completed', self.head_title)
        self.assertIn('/admin', self.get_elem(self.admin_login_link).get_attribute('href'))

        self.assertIn('/signup', self.get_elem(self.user_signup_link).get_attribute('href'))

        # Display app again now redirect to user login page
        self.visit(self.root_url)
        self.assertIn('login', self.head_title)


class AdminLoginTests(AdminLoginPage):
    def test_admin_user_can_login_in_django_admin(self):
        """Admin user can login in Django admin"""
        # Admin user have already setup org and admin
        setup_admin(setup_org())
        self.visit(self.url)

        # He log to admin portal
        self.log_admin()

        # Django admin display properly
        self.assertIn(f'welcome, {tv.ADMIN_EMAIL}', self.get_elem(self.django_admin_success_message).text.lower())


class FirstUserSignupTest(SignupPages):
    def test_user_can_signup_to_first_organization(self):
        """User can signup to first organization"""
        # Admin user have already setup org and admin
        # User go to signup page
        org = setup_org()
        setup_admin(org)

        self.visit_signup_page(org.slug)

        # The name of the first organization is displayed and user can create his account
        self.assertIn(tv.ORG_NAME_1, self.get_elem(self.page_title).text)
        self.create_user()

        # Success message appears when account creation is complete
        self.assertIn('account have been created', self.get_elem(self.main_panel).text)


class FirstUserLoginTest(LoginPage):
    def test_user_can_access_login_page_of_first_organization(self):
        """User access login page of first organization"""
        org = setup_org()
        setup_admin(org)
        setup_user(org)

        # First user display the login page
        self.visit(self.url)

        # The login page is properly displayed
        login_header = self.get_elem(self.page_title).text
        self.assertIn('login', login_header.lower())
