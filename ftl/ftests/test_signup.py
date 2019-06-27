from ftests.tools import test_values as tv
from ftests.pages.signup_pages import SignupPages
from ftests.tools.setup_helpers import setup_org, setup_admin


class SignupPageTests(SignupPages):
    def setUp(self, **kwargs):
        # first org and admin already created
        super().setUp()
        self.org_1 = setup_org(tv.ORG_NAME_1, tv.ORG_SLUG_1)
        setup_admin(org=self.org_1)
        self.org_2 = setup_org(tv.ORG_NAME_2, tv.ORG_SLUG_2)

    def test_signup_to_first_org(self):
        # User create an account in the first org
        self.visit_signup_page(self.org_1.slug)
        self.create_user(user_num=1)

        # Success page appears
        self.assertIn('succeed', self.head_title)
        self.assertIn('account have been created', self.get_elem(self.main_panel).text)

    def test_signup_to_second_org(self):
        # User create an account in the second org
        self.visit_signup_page(self.org_2.slug)
        self.create_user(user_num=2)

        # Success page appears
        self.assertIn('succeed', self.head_title)
        self.assertIn('account have been created', self.get_elem(self.main_panel).text)

    def test_signup_failed(self):
        # User try to create an account without filling fields
        self.visit_signup_page(self.org_1.slug)
        self.get_elem(self.submit_input).click()

        # The browser refused form submission as all fields are set to required
        self.assertIn('signup', self.head_title)
        self.assertIn('Create your account', self.get_elem(self.page_title).text)
