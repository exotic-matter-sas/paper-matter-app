import os

from ftl.settings import BASE_DIR
from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


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
    first_folder_button = '.folder'

    documents_list = '.document-thumbnail'
    first_document_title = '.document-title span'

    def search_document(self, search_text):
        self.get_elem(self.search_input).send_keys(search_text)
        self.get_elem(self.search_button).click()
        self.wait_for_element_to_disappear(self.document_list_loader)

    def upload_document(self, absolute_path=None):
        if not absolute_path:
            absolute_path = os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf')
        self.get_elem(self.document_upload_input, is_visible=False).send_keys(absolute_path)
        self.get_elem(self.submit_document_upload_button).click()
        self.wait_for_element_to_disappear(self.document_upload_loader)

    def create_folder(self, folder_name=tv.FOLDER1_NAME):
        self.get_elem(self.create_folder_button).click()
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.get_elem(self.modal_accept_button).click()

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()
