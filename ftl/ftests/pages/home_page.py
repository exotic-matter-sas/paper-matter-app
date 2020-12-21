#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import os

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv
from ftl.settings import BASE_DIR


class HomePage(BasePage):
    url = "/app/"

    search_input = "#search-input"
    search_button = "#search-button"
    add_documents_button = "#add-documents"
    document_list_loader = "#document-list-loader"

    profile_name = "#email"

    document_upload_input = 'input[type="file"]'
    document_upload_label = ".custom-file-label"
    submit_document_upload_button = "#upload-button"
    document_upload_loader = ".upload-tasks-loader"

    breadcrumb_first_folder = ".breadcrumb-item:first-child"
    breadcrumb_folders = ".breadcrumb-item"
    breadcrumb_current_folder = ".breadcrumb-item.active"

    refresh_documents_button = "#refresh-documents"

    create_folder_button = "#create-folder"
    manage_folders_button = "#manage-folders"
    folders_list_buttons = "button.folder > span:not(.spinner-border):not(.d-none)"
    folders_list_loader = "#folder-list-loader"

    sort_dropdown_button = "#documents-sort"
    az_sort_item = "#az-sort"
    za_sort_item = "#za-sort"
    recent_sort_item = "#recent-sort"
    older_sort_item = "#older-sort"
    relevance_sort_item = "#relevance-sort"

    batch_toolbar = "#action-selected-documents"
    unselect_all_docs_batch_button = "#unselect-all-documents"
    cancel_selection_button = "#cancel-selection"
    move_docs_batch_button = "#move-documents"
    delete_docs_batch_button = "#delete-documents"

    documents_list_container = "#documents-list"
    documents_thumbnails = ".document-thumbnail"
    documents_download_buttons = ".document-thumbnail .download-button"
    documents_checkboxes = ".document-thumbnail .custom-checkbox"
    documents_titles = ".document-thumbnail .card-title span"
    first_document_thumb = ".document-thumbnail:first-child"
    first_document_title = ".document-thumbnail:first-child .card-title span"
    first_document_date = ".document-thumbnail:first-child .card-footer small"
    last_document_title = ".document-thumbnail:last-child .card-title span"

    more_documents_button = "#more-documents"
    more_documents_loader = "#more-documents .loader"

    def wait_documents_list_loaded(self):
        self.wait_for_elem_to_disappear(self.document_list_loader)

    def wait_folder_list_loaded(self):
        self.wait_for_elem_to_disappear(self.folders_list_loader)

    def wait_more_documents_loaded(self):
        self.wait_for_elem_to_disappear(self.more_documents_loader)

    def search_documents(self, search_text):
        self.get_elem(self.search_input).clear()
        self.get_elem(self.search_input).send_keys(search_text)
        self.get_elem(self.search_button).click()
        self.wait_documents_list_loaded()

    def upload_documents(self, absolute_paths=None):
        if not absolute_paths:
            absolute_paths = os.path.join(
                BASE_DIR, "ftests", "tools", "test_documents", "test.pdf"
            )
        else:
            if type(absolute_paths) is not list:
                absolute_paths = [absolute_paths]
            absolute_paths = "\n".join(absolute_paths)

        self.get_elem(self.document_upload_input, is_visible=False).send_keys(
            absolute_paths
        )
        self.wait_for_elem_to_disappear(self.document_upload_loader, timeout=10)
        # Needed in case of several upload in a row as upload success trigger a notification that hide upload button
        self.close_all_notifications()

    def rename_document_from_list(self, doc_elem, doc_name):
        doc_elem.click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(doc_name)
        self.accept_modal()

    def create_folder(self, folder_name=tv.FOLDER1_NAME, close_notification=True):
        self.get_elem(self.create_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.accept_modal()
        if close_notification:
            self.close_all_notifications()

    def refresh_documents_list(self):
        self.get_elem(self.refresh_documents_button).click()
        self.wait_documents_list_loaded()

    def open_first_document(self):
        first_document_thumb = self.get_elem(self.first_document_thumb)
        first_document_thumb.click()
        self.wait_for_elem_to_show(self.document_viewer_panel)

    def select_documents(self, documents_names):
        documents_list = self.get_elems(self.documents_thumbnails)
        for document in documents_list:
            if (
                document.find_element_by_css_selector(self.documents_titles).text
                in documents_names
            ):
                document.find_element_by_css_selector(self.documents_checkboxes).click()
        self.wait_for_elem_to_show(self.batch_toolbar)

    def sort_documents_list(self, sort_type):
        allowed_sort_type = ["az", "za", "recent", "older", "relevance"]
        if sort_type not in allowed_sort_type:
            raise ValueError(
                f"Invalid value for sort_type, allowed values are {allowed_sort_type}"
            )

        self.get_elem(self.sort_dropdown_button).click()

        sort_item = getattr(self, f"{sort_type}_sort_item")
        self.wait_for_elem_to_show(sort_item)
        self.get_elem(sort_item).click()

        self.wait_documents_list_loaded()
