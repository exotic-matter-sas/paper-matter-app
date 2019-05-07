from ftests.tools import test_values as tv
from ftests.pages.django_admin_home_page import AdminHomePage
from ftests.pages.django_admin_login_page import AdminLoginPage
from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.signup_pages import SignupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user


class InitialSetupTest(SetupPages, SignupPages, LoginPage, HomePage):
    def test_end_to_end_setup(self):
        # Admin have just install ftl-app and display it for the first time
        self.visit(self.root_url)

        # Admin fulfill the org creation form
        self.create_first_organization()

        # Admin fulfill the admin creation form
        self.create_admin()

        # Admin copy the link for user signup and send it to the first user
        user_signup_link = self.get_elem(self.user_signup_link).get_attribute('href')

        # Admin close its browser
        self.browser.quit()

        # First user display the app for the first time using the link sent by Admin
        self.setUp()
        self.visit(user_signup_link, absolute_url=True)

        # First user fulfill the user creation form
        username = self.create_user()

        # First user login to the first organization
        self.get_elem(self.user_login_link).click()
        self.log_user()

        # First user is properly logged
        self.assertIn('home', self.head_title)
        self.assertIn(username, self.get_elem(self.profile_name).text)


class SecondOrgSetup(AdminLoginPage, AdminHomePage, SignupPages, LoginPage, HomePage):
    def test_second_org_setup(self):
        # first org, admin, first user are already created
        org1 = setup_org()
        setup_admin(org=org1)
        setup_user(org=org1)

        # Admin user login to admin portal and create a new org
        self.visit(AdminLoginPage.url)
        self.log_admin()
        self.get_elem(self.create_org_link).click()
        org2_slug = self.create_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)

        # Admin close its browser
        self.browser.quit()

        # Second user display the app for the first time to create its account
        self.setUp()
        self.visit_signup_page(org2_slug)

        # Second user fulfill the user creation form
        username = self.create_user(user_num=2)

        # Second user login to the second organization
        self.get_elem(self.user_login_link).click()
        self.log_user(user_num=2)

        # Second user is properly logged
        self.assertIn('home', self.head_title)
        self.assertIn(username, self.get_elem(self.profile_name).text)


class NewUserAddDocumentInsideFolder(SignupPages, LoginPage, HomePage):
    def test_new_user_add_document_inside_folder(self):
        # first org, admin, are already created
        org = setup_org()
        setup_admin(org=org)

        # First user create its account and login
        self.visit_signup_page(org.slug)
        self.create_user()
        self.get_elem(self.user_login_link).click()
        self.log_user()

        # First user add a folder, a document inside it and display document
        self.create_folder()
        self.get_elem(self.first_folder_button).click()
        self.upload_document()
        self.get_elem(self.first_document_title).click()

        # User can see the uploaded document inside the viewer
        pdf_viewer_iframe = self.browser.find_element_by_css_selector('.doc-view-modal iframe')
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.browser.find_element_by_css_selector('title').get_attribute("innerHTML")

        self.assertEqual(pdf_viewer_iframe_title, 'PDF.js viewer')
