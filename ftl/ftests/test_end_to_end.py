#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
from unittest import skipIf, skip
from unittest.mock import patch

from django import db
from django.conf import settings
from django.core import mail
from django.db.models import Func, F
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from selenium.common.exceptions import NoSuchElementException

from core import views
from core.models import FTLDocument
from core.processing.ftl_processing import FTLDocumentProcessing
from ftests.pages.account_pages import AccountPages
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.django_admin_home_page import AdminHomePage
from ftests.pages.django_admin_login_page import AdminLoginPage
from ftests.pages.document_viewer_modal import DocumentViewerModal
from ftests.pages.home_page import HomePage
from ftests.pages.setup_pages import SetupPages
from ftests.pages.signup_pages import SignupPages
from ftests.pages.user_login_page import LoginPage
from ftests.test_account import (
    mocked_verify_user,
    totp_time_setter,
    mocked_totp_time_setter,
    totp_time_property,
    TotpDevice2FATests,
)
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_2fa_fido2_device,
    setup_2fa_totp_device,
)
from ftl.settings import BASE_DIR


class InitialSetupTest(SetupPages, SignupPages, LoginPage, HomePage):
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    @skip("Multi users feature disabled")
    def test_end_to_end_setup(self):
        # Admin have just install Paper Matter and display it for the first time
        self.visit(self.root_url)

        # Admin fulfill the admin creation form
        self.create_first_org_and_admin()

        # Admin copy the link for user signup and send it to the first user
        user_signup_link = self.get_elem(self.user_signup_link).get_attribute("href")

        # Admin close its browser
        self.browser.quit()

        # First user display the app for the first time using the link sent by Admin
        self.setUp()
        self.visit(user_signup_link, absolute_url=True)

        # First user fulfill the user creation form
        email = self.create_user(activate_user=True)

        self.assertEqual(len(mail.outbox), 1)

        # First user login to the first organization
        self.log_user()

        # First user is properly logged
        self.assertIn("home", self.head_title)
        self.assertIn(email, self.get_elem(self.profile_name).text)


class SecondOrgSetup(AdminLoginPage, AdminHomePage, SignupPages, LoginPage, HomePage):
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    @skip("Multi users feature disabled")
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
        email = self.create_user(user_num=2, activate_user=True)

        # Second user login to the second organization
        self.log_user(user_num=2)

        # Second user is properly logged
        self.assertIn("home", self.head_title)
        self.assertIn(email, self.get_elem(self.profile_name).text)


class NewUserAddDocumentInsideFolder(
    SignupPages, LoginPage, HomePage, DocumentViewerModal
):
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    @patch.object(FTLDocumentProcessing, "apply_processing")
    @skip("Multi users feature disabled")
    def test_new_user_add_document_inside_folder(self, mock_apply_processing):
        # first org, admin, are already created
        org = setup_org()
        setup_admin(org=org)

        # First user create its account and login
        self.visit_signup_page(org.slug)
        self.create_user(activate_user=True)
        self.log_user()

        # First user add a folder, a document inside it and display document
        self.create_folder()
        self.get_elem(self.folders_list_buttons).click()
        self.upload_documents()
        self.get_elem(self.first_document_title).click()

        # User can see the uploaded document inside the viewer
        # User can see the pdf inside the pdf viewer
        self.wait_for_elem_to_show(self.pdf_viewer_iframe)
        pdf_viewer_iframe = self.get_elem(self.pdf_viewer_iframe)
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.get_elem("title", False).get_attribute(
            "innerHTML"
        )

        self.assertEqual(pdf_viewer_iframe_title, "PDF.js viewer")


class TikaDocumentIndexationAndSearch(LoginPage, HomePage, DocumentViewerModal):
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
        super().tearDown()

    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    def test_upload_doc_wait_tika_indexation_and_search_for_doc(self):
        # User upload 2 documents
        self.upload_documents()
        second_document_title = "green"
        self.upload_documents(
            os.path.join(
                BASE_DIR,
                "ftests",
                "tools",
                "test_documents",
                second_document_title + ".pdf",
            )
        )

        # User wait for document to be indexed
        # TODO replace by a wait_for_element_to_disappear when a indexing indicator is implemented
        queryset = FTLDocument.objects.annotate(
            tsvector_length=Func(F("tsvector"), function="length")
        )

        def query_set_validator(query_set):
            if len(query_set) == 2:
                return True
            else:
                return False

        self._wait_for_method_to_return(
            queryset.filter,
            60,
            custom_return_validator=query_set_validator,
            tsvector_length__gt=0,
        )

        # User search last uploaded document
        self.search_documents(second_document_title)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(
            second_document_title, self.get_elem(self.first_document_title).text
        )

    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    def test_search_renamed_doc(self):
        # User upload 2 documents
        self.upload_documents()
        second_document_title = "green.pdf"
        self.upload_documents(
            os.path.join(
                BASE_DIR, "ftests", "tools", "test_documents", second_document_title
            )
        )

        # User wait for document to be indexed
        # TODO replace by a wait_for_element_to_disappear when a indexing indicator is implemented
        queryset = FTLDocument.objects.annotate(
            tsvector_length=Func(F("tsvector"), function="length")
        )

        def query_set_validator(query_set):
            if len(query_set) == 2:
                return True
            else:
                return False

        self._wait_for_method_to_return(
            queryset.filter,
            60,
            custom_return_validator=query_set_validator,
            tsvector_length__gt=0,
        )

        # Refresh page to display documents
        self.visit(HomePage.url)

        # User open second document and rename it
        self.get_elem(self.first_document_title).click()
        new_title = "bingo!"
        self.rename_document(new_title)
        self.close_document()

        # user search for document using its new title
        self.search_documents(new_title)

        # the second uploaded document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(new_title, self.get_elem_text(self.first_document_title))


class UserSetupAll2FA(LoginPage, AccountPages):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged to 2FA account page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

        self.visit(LoginPage.url)
        self.log_user()
        self.visit(AccountPages.two_factors_authentication_url)

    @patch.object(TOTP, "time", totp_time_property)
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    def test_user_setup_all_2fa(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # User add an auth app (can't be really added in this test)
        setup_2fa_totp_device(self.user, secret_key=TotpDevice2FATests.secret_key)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # User add emergency code too
        self.add_emergency_codes_set("My emergency codes")

        # Finally, user add a security key (can't be really added in this test)
        setup_2fa_fido2_device(self.user)
        self.visit(AccountPages.two_factors_authentication_url)  # refresh page

        # The 3 2FA devices appears in the list
        self.assertEqual(1, len(self.get_elems(self.auth_app_divs)))
        self.assertEqual(1, len(self.get_elems(self.emergency_codes_divs)))
        self.assertEqual(1, len(self.get_elems(self.security_key_divs)))

        # User logout and login
        self.get_elem(self.logout_button).click()
        self.middleware_patcher.stop()  # Remove middleware mock, to restore check pages
        self.log_user()

        # The 2FA check page appears with all device available
        self.assertEqual(2, len(self.get_elems(self.check_pages_alternatives_list)))

        # Login using totp
        for i, item_text in enumerate(
            self.get_elems_text(self.check_pages_alternatives_list)
        ):
            if "authentication app" in item_text:
                self.get_elems(self.check_pages_alternatives_list)[i].click()
        self.enter_2fa_code(TotpDevice2FATests.valid_token)
        self.assertIn("home", self.head_title)

        # user delete its security key 2FA
        self.visit(self.two_factors_authentication_url)
        # User delete existing security key
        self.get_elems(self.delete_security_key_buttons)[0].click()

        # There is no special warning about it, as there is auth app 2fa left
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.delete_warning)
