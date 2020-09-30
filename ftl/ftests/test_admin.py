#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from selenium.common.exceptions import NoSuchElementException

from ftests.pages.django_admin_pages import AdminPages
from ftests.pages.login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_temporary_file,
    setup_document_share,
)


class AdminPreserveUserPrivacy(LoginPage, AdminPages):
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

        # admin, user1 and user2 have added documents, some documents are shared
        self.admin_resources = {}
        self.admin_resources["doc1"] = setup_document(
            self.admin_org, ftl_user=self.admin, binary=setup_temporary_file().name
        )
        self.admin_resources["doc2"] = setup_document(
            self.admin_org, ftl_user=self.admin, binary=setup_temporary_file().name,
        )
        self.admin_resources["doc3"] = setup_document(
            self.admin_org, ftl_user=self.admin, binary=setup_temporary_file().name,
        )
        self.admin_resources["share_links"] = [
            setup_document_share(self.admin_resources["doc3"])
        ]

        self.user1_resources = {}
        self.user1_resources["doc1"] = setup_document(
            self.user1_org, ftl_user=self.user1, binary=setup_temporary_file().name
        )
        self.user1_resources["doc2"] = setup_document(
            self.user1_org, ftl_user=self.user1, binary=setup_temporary_file().name,
        )
        self.user1_resources["doc3"] = setup_document(
            self.user1_org, ftl_user=self.user1, binary=setup_temporary_file().name,
        )
        self.user1_resources["share_links"] = [
            setup_document_share(self.user1_resources["doc2"])
        ]

        self.user2_resources = {}
        self.user2_resources["doc1"] = setup_document(
            self.user2_org, ftl_user=self.user2
        )
        self.user2_resources["doc2"] = setup_document(
            self.user2_org, ftl_user=self.user2,
        )
        self.user2_resources["doc3"] = setup_document(
            self.user2_org, ftl_user=self.user2,
        )
        self.user2_resources["share_links"] = [
            setup_document_share(self.user2_resources["doc1"])
        ]

    def test_admin_portal_show_limited_data(self):
        allowed_models = [
            "Groups",
            "Access attempts",
            "Access logs",
            "Ftl document sharings",
            "Ftl documents",
            "Ftl orgs",
            "Users",
            "Applications",
        ]
        document_non_personal_data = [
            "pid",
            "created",
            "edited",
            "size",
            "md5",
            "deleted",
            "ocrized",
            "ocr_retry",
            "type",
        ]
        user_non_personal_data = [
            "org",
            "email",
            "password",  # (hash)
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
        ]
        document_sharing_non_personal_data = [
            "pid",
            "created",
            "edited",
            "expire_at",
            "password",  # not yet implemented, but may be required in case of abuse report to check legality of document
        ]

        # Admin user log into admin portal
        self.visit(AdminPages.url)
        self.log_user(email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS)

        # Admin can only see a limited list of models
        models_list = self.get_elems_text(self.model_list)
        self.assertCountEqual(models_list, allowed_models)

        # Admin user CAN'T LIST all documents
        self.visit(AdminPages.ftl_documents_url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)

        # Admin user CAN'T SEARCH existing documents using partial pid or partial/full title or partial/full content
        self.search_admin_list(str(self.user1_resources["doc1"].pid)[:1])
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()
        self.search_admin_list(self.user1_resources["doc1"].title[:1])
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()
        self.search_admin_list(self.user1_resources["doc1"].title)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()
        self.search_admin_list(self.user1_resources["doc1"].content_text.split(" ")[0])
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()
        self.search_admin_list(self.user1_resources["doc1"].content_text)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()

        # Admin user CAN SEARCH existing documents using full pid
        self.search_admin_list(str(self.user1_resources["doc1"].pid))
        # Admin display details of document
        self.get_elem(self.admin_first_row_details_link).click()
        # Only non personal document data are shown
        for k, v in vars(self.user1_resources["doc1"]).items():
            # Ignore internal attributes and attributes not relevant
            if not k.startswith("_") and k not in ["id"]:
                # Non personal data should be present
                if k in document_non_personal_data:
                    self.get_elem(f".field-{k}")
                # Personal data must NOT be present
                else:
                    with self.assertRaises(NoSuchElementException):
                        self.get_elem(f".field-{k}")

        # Admin user CAN'T LIST all users
        self.visit(AdminPages.ftl_users_url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)

        # Admin user CAN'T SEARCH existing users using partial email
        self.search_admin_list(self.user1.email[:1])
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()

        # Admin user CAN SEARCH existing users using full email
        self.search_admin_list(self.user1.email)
        # Admin display details of user
        self.get_elem(self.admin_first_row_details_link).click()

        # Only non personal document data are shown
        for k, v in vars(self.user1).items():
            # Ignore internal attributes and attributes not relevant
            if not k.startswith("_") and k not in ["id"]:
                # Non personal data should be present
                if k in user_non_personal_data:
                    self.get_elem(f".field-{k}")
                # Personal data must NOT be present
                else:
                    with self.assertRaises(NoSuchElementException):
                        self.get_elem(f".field-{k}")

        # Admin user CAN'T LIST all document sharing
        self.visit(AdminPages.ftl_document_sharings_url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)

        # Admin user CAN'T SEARCH document sharing using partial pid or full note
        self.search_admin_list(str(self.user2_resources["share_links"][0].pid)[:1])
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()
        self.search_admin_list(str(self.user2_resources["share_links"][0].note))
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.admin_results_list)
        self.previous_page()

        # Admin user CAN SEARCH document sharing using full pid
        self.search_admin_list(str(self.user2_resources["share_links"][0].pid))
        # Admin display details of document sharing
        self.get_elem(self.admin_first_row_details_link).click()

        # Only non personal document sharing data are shown
        for k, v in vars(self.user1).items():
            # Ignore internal attributes and attributes not relevant
            if not k.startswith("_") and k not in ["id"]:
                # Non personal data should be present
                if k in document_sharing_non_personal_data:
                    self.get_elem(f".field-{k}")
                # Personal data must NOT be present
                else:
                    with self.assertRaises(NoSuchElementException):
                        self.get_elem(f".field-{k}")
