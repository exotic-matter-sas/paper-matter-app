#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
from core.models import FTLOrg
from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class AdminPages(BasePage):
    url = "/admin/"
    ftl_documents_url = "/admin/core/ftldocument/"
    ftl_document_sharings_url = "/admin/core/ftldocumentsharing/"
    ftl_users_url = "/admin/core/ftluser/"

    page_title = "h1"
    model_list = 'tr[class^="model-"] th'

    submit_input = 'input[type="submit"].default'

    # Generic list
    admin_search_list_input = "#searchbar"
    admin_search_list_submit = '#changelist-search [type="submit"]'
    admin_results_list = "#result_list tbody tr"
    admin_first_row_details_link = "#result_list tbody tr:first-child a"

    # Generic details form
    admin_details_from = 'form[action*="changelist"]'

    # Create org
    create_org_link = ".model-ftlorg a.addlink"
    org_name_input = "#id_name"
    org_slug_input = "#id_slug"

    # Create user
    create_user_link = ".model-ftluser a.addlink"
    org_id_input = "#id_org"
    user_email_input = "#id_email"
    user_password_input = "#id_password1"
    user_password_confirmation_input = "#id_password2"
    user_staff_checkbox = "#id_is_staff"
    user_superuser_checkbox = "#id_is_superuser"

    def create_org(self, name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1):
        org_name_input = self.get_elem(self.org_name_input)
        org_slug_input = self.get_elem(self.org_slug_input)
        submit_input = self.get_elem(self.submit_input)

        org_name_input.send_keys(name)
        org_slug_input.send_keys(slug)
        submit_input.click()

        return slug

    def create_user(
        self,
        org_slug=tv.ORG_SLUG_1,
        email=tv.USER1_EMAIL,
        password=tv.USER1_PASS,
        is_admin=False,
    ):
        org_name_input = self.get_elem(self.org_id_input)
        user_email_input = self.get_elem(self.user_email_input)
        user_password_input = self.get_elem(self.user_password_input)
        user_password_confirmation_input = self.get_elem(
            self.user_password_confirmation_input
        )
        submit_input = self.get_elem(self.submit_input)

        org_id = FTLOrg.objects.get(slug=org_slug).id
        org_name_input.send_keys(org_id)
        user_email_input.send_keys(email)
        user_password_input.send_keys(password)
        user_password_confirmation_input.send_keys(password)
        submit_input.click()

        if is_admin:
            user_staff_checkbox = self.get_elem(self.user_staff_checkbox)
            user_superuser_checkbox = self.get_elem(self.user_superuser_checkbox)
            submit_input = self.get_elem(self.submit_input)

            user_staff_checkbox.click()
            user_superuser_checkbox.click()
            submit_input.click()

        return email

    def search_admin_list(self, search_value):
        self.get_elem(self.admin_search_list_input).clear()
        self.get_elem(self.admin_search_list_input).send_keys(search_value)
        self.get_elem(self.admin_search_list_submit).click()
