import os

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv
from ftl.settings import BASE_DIR


class HomePage(BasePage):
    url = '/app/'

    search_input = '#search-input'
    search_button = '#search-button'
    document_list_loader = '#document-list-loader'

    profile_name = '#username'

    document_upload_input = 'input[type="file"]'
    document_upload_label = '.custom-file-label'
    submit_document_upload_button = '#upload-button'
    document_upload_loader = '#document-upload-loader'

    refresh_documents_button = '#refresh-documents'

    create_folder_button = '#create-folder'
    first_folder_button = 'button.folder > span:not(.spinner-border):not(.d-none)'
    folder_list_loader = '#folder-list-loader'

    documents_list = '#documents-list'
    documents_thumbnails = '.document-thumbnail'
    first_document_title = '.document-title span'

    def wait_document_list_loaded(self):
        self.wait_for_elem_to_disappear(self.document_list_loader)

    def wait_folder_list_loaded(self):
        self.wait_for_elem_to_disappear(self.folder_list_loader)

    def search_document(self, search_text):
        self.get_elem(self.search_input).send_keys(search_text)
        self.get_elem(self.search_button).click()
        self.wait_document_list_loaded()

    def upload_document(self, absolute_path=None):
        if not absolute_path:
            absolute_path = os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf')
        self.get_elem(self.document_upload_input, is_visible=False).send_keys(absolute_path)
        self.get_elem(self.submit_document_upload_button).click()
        self.wait_for_elem_to_disappear(self.document_upload_loader)
        # Needed in case of several upload in a row as upload success trigger a notification that hide upload button
        self.close_last_notification()

    def create_folder(self, folder_name=tv.FOLDER1_NAME):
        self.get_elem(self.create_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.get_elem(self.modal_accept_button).click()
        self.close_last_notification()

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()
