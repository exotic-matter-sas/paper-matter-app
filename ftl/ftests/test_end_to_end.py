#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
import threading
from unittest import skipIf, skip
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import override_settings
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from selenium.common.exceptions import NoSuchElementException

from core.tasks import apply_ftl_processing
from ftests.pages.account_pages import AccountPages
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.django_admin_home_page import AdminHomePage
from ftests.pages.django_admin_login_page import AdminLoginPage
from ftests.pages.document_viewer_modal import DocumentViewerModal
from ftests.pages.home_page import HomePage
from ftests.pages.move_documents_modal import MoveDocumentsModal
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
    setup_document,
    setup_folder,
    setup_2fa_static_device,
    setup_temporary_file,
)
from ftl import celery
from ftl.celery import app


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
    @patch.object(apply_ftl_processing, "delay")
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
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


@override_settings(CELERY_BROKER_URL="memory://localhost")
class TikaDocumentIndexationAndSearch(LoginPage, HomePage, DocumentViewerModal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.control.purge()
        cls._worker = app.Worker(app=app, pool="solo", concurrency=1)
        cls._thread = threading.Thread(target=cls._worker.start)
        cls._thread.daemon = True
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        cls._worker.stop()
        super().tearDownClass()

    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

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
                settings.BASE_DIR,
                "ftests",
                "tools",
                "test_documents",
                second_document_title + ".pdf",
            )
        )

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

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
                settings.BASE_DIR,
                "ftests",
                "tools",
                "test_documents",
                second_document_title,
            )
        )

        # Refresh page to display documents
        self.visit(HomePage.url)

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

        # User open second document and rename it
        self.get_elem(self.first_document_thumb).click()
        new_title = "bingo!"
        self.rename_document(new_title)
        self.close_document()

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

        # user search for document using its new title
        self.search_documents(new_title)

        # the second uploaded document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(new_title, self.get_elem_text(self.first_document_title))


@override_settings(CELERY_BROKER_URL="memory://localhost")
class TikaDocumentIndexationEdgeCases(LoginPage, HomePage, DocumentViewerModal, MoveDocumentsModal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.control.purge()
        cls._worker = app.Worker(app=app, pool="solo", concurrency=1)
        cls._thread = threading.Thread(target=cls._worker.start)
        cls._thread.daemon = True
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        cls._worker.stop()
        super().tearDownClass()

    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.folder = setup_folder(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    def test_search_a_doc_renamed_during_its_processing(self):
        # User upload a document
        old_title = "green"
        self.upload_documents(
            os.path.join(
                settings.BASE_DIR,
                "ftests",
                "tools",
                "test_documents",
                old_title + ".pdf",
                )
        )

        # User rename document from list
        doc_to_rename = self.get_elem(self.first_document_title)
        new_title = "bingo!"
        self.rename_document_from_list(doc_to_rename, new_title)

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

        # User search for document using its old title
        self.search_documents(old_title)

        # No document appears
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 0,
                         "Document should have been renamed and not appears in the list")

        # User search for document using its new title
        self.search_documents(new_title)

        # The document has been properly renamed
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1,
                         "Document should have been renamed and appears in the list")

    def test_search_a_doc_annotated_during_its_processing(self):
        # User upload a document
        self.upload_documents()

        # User annotate doc just after upload
        self.open_first_document()

        new_doc_note = "bingo!"
        self.annotate_document(new_doc_note)
        self.close_document()

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

        # User search for document using its note
        self.search_documents(new_doc_note)

        # The document has been properly renamed
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1,
                         "Document should have been renamed and appears in the list")

    def test_move_a_doc_during_its_processing(self):
        # User upload a document
        doc_title = "green"
        self.upload_documents(
            os.path.join(
                settings.BASE_DIR,
                "ftests",
                "tools",
                "test_documents",
                doc_title + ".pdf",
                )
        )

        # User move document during its processing
        self.open_first_document()
        self.get_elem(self.move_document_button).click()
        self.move_document(self.folder.name)
        self.close_document()

        # User wait for document to be indexed
        self.wait_celery_queue_to_be_empty(self._worker)

        # User see the documents in the proper folder
        self.get_elem(self.folders_list_buttons).click()
        self.wait_documents_list_loaded()
        self.assertCountEqual([doc_title], self.get_elems_text(self.documents_titles),
                              "Document should have been moved to proper folder")


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
        self.visit(LoginPage.logout_url)
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


class AccountDeletion(LoginPage, AccountPages, AdminLoginPage, AdminHomePage):
    def setUp(self, **kwargs):
        # orgs, admin, users are already created
        super().setUp()
        self.admin_org = setup_org(name="admin-org", slug="admin-org")
        self.admin = setup_admin(self.admin_org)
        self.user1_org = setup_org(name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1)
        self.user1 = setup_user(
            self.user1_org, email=tv.USER1_EMAIL, password=tv.USER1_PASS
        )
        self.user2_org = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        self.user2 = setup_user(
            self.user2_org, email=tv.USER2_EMAIL, password=tv.USER2_PASS
        )

        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

        # admin, user1 and user2 have added documents, folders, otp devices
        self.admin_resources = {}
        self.admin_resources["folder1"] = setup_folder(self.admin_org)
        self.admin_resources["sub_folder1"] = setup_folder(
            self.admin_org, parent=self.admin_resources["folder1"]
        )
        self.admin_resources["doc1"] = setup_document(
            self.admin_org, ftl_user=self.admin, binary=setup_temporary_file().name
        )
        self.admin_resources["doc2"] = setup_document(
            self.admin_org,
            ftl_user=self.admin,
            ftl_folder=self.admin_resources["folder1"],
            binary=setup_temporary_file().name,
        )
        self.admin_resources["doc3"] = setup_document(
            self.admin_org,
            ftl_user=self.admin,
            ftl_folder=self.admin_resources["sub_folder1"],
            binary=setup_temporary_file().name,
        )
        self.admin_resources["totp_device"] = setup_2fa_totp_device(
            self.admin, secret_key=TotpDevice2FATests.secret_key
        )
        self.admin_resources["fido2_device"] = setup_2fa_fido2_device(self.admin)
        self.admin_resources["static_device"] = setup_2fa_static_device(
            self.admin, codes_list=["AAA"]
        )

        self.user1_resources = {}
        self.user1_resources["folder1"] = setup_folder(self.user1_org)
        self.user1_resources["sub_folder1"] = setup_folder(
            self.user1_org, parent=self.user1_resources["folder1"]
        )
        self.user1_resources["doc1"] = setup_document(
            self.user1_org, ftl_user=self.user1, binary=setup_temporary_file().name
        )
        self.user1_resources["doc2"] = setup_document(
            self.user1_org,
            ftl_user=self.user1,
            ftl_folder=self.user1_resources["folder1"],
            binary=setup_temporary_file().name,
        )
        self.user1_resources["doc3"] = setup_document(
            self.user1_org,
            ftl_user=self.user1,
            ftl_folder=self.user1_resources["sub_folder1"],
            binary=setup_temporary_file().name,
        )
        self.user1_resources["totp_device"] = setup_2fa_totp_device(
            self.user1, secret_key=TotpDevice2FATests.secret_key
        )
        self.user1_resources["fido2_device"] = setup_2fa_fido2_device(self.user1)
        self.user1_resources["static_device"] = setup_2fa_static_device(
            self.user1, codes_list=["AAA"]
        )

        self.user2_resources = {}
        self.user2_resources["folder1"] = setup_folder(self.user2_org)
        self.user2_resources["sub_folder1"] = setup_folder(
            self.user2_org, parent=self.user2_resources["folder1"]
        )
        self.user2_resources["doc1"] = setup_document(
            self.user2_org, ftl_user=self.user2
        )
        self.user2_resources["doc2"] = setup_document(
            self.user2_org,
            ftl_user=self.user2,
            ftl_folder=self.user2_resources["folder1"],
        )
        self.user2_resources["doc3"] = setup_document(
            self.user2_org,
            ftl_user=self.user2,
            ftl_folder=self.user2_resources["sub_folder1"],
        )
        self.user2_resources["totp_device"] = setup_2fa_totp_device(
            self.user2, secret_key=TotpDevice2FATests.secret_key
        )
        self.user2_resources["fido2_device"] = setup_2fa_fido2_device(self.user2)
        self.user2_resources["static_device"] = setup_2fa_static_device(
            self.user2, codes_list=["AAA"]
        )

    @patch.object(TOTP, "time", totp_time_property)
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    @patch.object(celery.app, "send_task")
    def test_all_user_resources_are_deleted(self, mocked_send_task_delete_document):
        # user is already logged to account deletion page
        self.visit(LoginPage.url)
        self.log_user(user_num=1)
        self.visit(AccountPages.delete_account_url)

        # User submit account deletion form
        self.delete_account(tv.USER1_PASS)

        # Faking the hourly /etc/cron.hourly/batch-delete-documents CRON call
        self.client.get(
            f"/crons/{settings.CRON_SECRET_KEY}/batch-delete-documents",
            HTTP_X_APPENGINE_CRON="true",
        )
        # Faking the daily CRON /etc/cron.daily/batch-delete-orgs
        self.client.get(
            f"/crons-account/{settings.CRON_SECRET_KEY}/batch-delete-orgs",
            HTTP_X_APPENGINE_CRON="true",
        )

        # All resources from user1 are deleted
        for resource in self.user1_resources.values():
            with self.assertRaises(
                resource.DoesNotExist,
                msg="All user1 resources should have been deleted alongside with its account",
            ):
                resource.refresh_from_db()

        # All resources from user2 are still present
        for resource in self.user2_resources.values():
            resource.refresh_from_db()

    @patch.object(TOTP, "time", totp_time_property)
    @skipIf(
        settings.DEV_MODE and not NODE_SERVER_RUNNING,
        "Node not running, this test can't be run",
    )
    @patch.object(celery.app, "send_task")
    def test_unique_admin_can_create_a_second_admin_and_delete_its_account(
        self, mocked_send_task_delete_document
    ):
        # Admin is already logged to account deletion page
        self.visit(LoginPage.url)
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)
        self.visit(AccountPages.delete_account_url)

        # Admin try to delete its account but can't as he is the only instance admin
        self.assertIn(
            "holds the last administrator", self.get_elem_text(self.error_message),
        )
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.submit_account_deletion)

        # Admin go to admin panel and create a new org and admin user in this org
        self.visit(AdminLoginPage.url)
        self.get_elem(self.create_org_link).click()
        admin_org2_slug = self.create_org("admin-org2", "admin-org2")
        self.visit(AdminLoginPage.url)
        self.get_elem(self.create_user_link).click()
        self.create_user(
            admin_org2_slug, tv.ADMIN2_EMAIL, tv.ADMIN2_PASS, is_admin=True
        )

        # Admin come back to account deletion page and can now delete its account
        self.visit(AccountPages.delete_account_url)
        self.delete_account(tv.ADMIN1_PASS)

        # Faking the hourly /etc/cron.hourly/batch-delete-documents CRON call
        self.client.get(
            f"/crons/{settings.CRON_SECRET_KEY}/batch-delete-documents",
            HTTP_X_APPENGINE_CRON="true",
        )
        # Faking the daily CRON /etc/cron.daily/batch-delete-orgs
        self.client.get(
            f"/crons-account/{settings.CRON_SECRET_KEY}/batch-delete-orgs",
            HTTP_X_APPENGINE_CRON="true",
        )

        # All resources from Admin are deleted
        for resource in self.admin_resources.values():
            with self.assertRaises(
                resource.DoesNotExist,
                msg="All Admin resources should have been deleted alongside with its account",
            ):
                resource.refresh_from_db()

        # All resources from user1 and user2 are still present
        for resource in self.user1_resources.values():
            resource.refresh_from_db()
        for resource in self.user2_resources.values():
            resource.refresh_from_db()
