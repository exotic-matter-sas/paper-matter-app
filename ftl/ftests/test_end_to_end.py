import os
from unittest import skipIf
from unittest.mock import patch

from django import db
from django.db.models import Func, F
from tika import parser

from core import views
from core.models import FTLDocument
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.django_admin_home_page import AdminHomePage
from ftests.pages.django_admin_login_page import AdminLoginPage
from ftests.pages.document_viewer_page import DocumentViewPage
from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.signup_pages import SignupPages
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user
from ftl.settings import BASE_DIR, DEV_MODE


class InitialSetupTest(SetupPages, SignupPages, LoginPage, HomePage):
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
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
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
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


class NewUserAddDocumentInsideFolder(SignupPages, LoginPage, HomePage, DocumentViewPage):
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(parser, 'from_file')
    def test_new_user_add_document_inside_folder(self, mock_tika_parser):
        mock_tika_parser.return_value = ""

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
        self.get_elem(self.folders_list_buttons).click()
        self.upload_document()
        self.get_elem(self.first_document_title).click()

        # User can see the uploaded document inside the viewer
        # User can see the pdf inside the pdf viewer
        pdf_viewer_iframe = self.get_elem(self.pdf_viewer)
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.get_elem('title', False).get_attribute("innerHTML")

        self.assertEqual(pdf_viewer_iframe_title, 'PDF.js viewer')


class TikaDocumentIndexationAndSearch(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    def tearDown(self):
        """ Additional teardown required to shutdown indexation thread and associated DB connection"""
        views.ftl_doc_processing.executor.submit(db.connections.close_all)
        views.ftl_doc_processing.executor.shutdown()
        super().tearDown()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_upload_doc_wait_tika_indexation_and_search_for_doc(self):
        # User upload 2 documents
        self.upload_document()
        second_document_title = 'green.pdf'
        self.upload_document(os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', second_document_title))

        # User wait for document to be indexed
        # TODO replace by a wait_for_element_to_disappear when a indexing indicator is implemented
        queryset = FTLDocument.objects.annotate(tsvector_length=Func(F('tsvector'), function='length'))

        def query_set_validator(query_set):
            if len(query_set) == 2:
                return True
            else:
                return False

        self._wait_for_method_to_return(queryset.filter, 60, custom_return_validator=query_set_validator,
                                        tsvector_length__gt=0)

        # User search last uploaded document
        self.search_document(second_document_title)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(second_document_title, self.get_elem(self.first_document_title).text)
