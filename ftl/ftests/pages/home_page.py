import os

from ftl.settings import BASE_DIR
from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class HomePage(BasePage):
    url = '/app/'

    profile_name = '#username'

    document_upload_input = 'input[type="file"]'
    document_upload_label = '.custom-file-label'
    submit_document_upload_button = '#upload-button'

    refresh_documents_button = '#refresh-documents'

    create_folder_button = '#create-folder'
    first_folder_button = '.folder'

    first_document_title = '.document-title span'

    def upload_document(self, absolute_path=None):
        if not absolute_path:
            absolute_path = os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf')
        self.get_elem(self.document_upload_input).send_keys(absolute_path)
        self.get_elem(self.submit_document_upload_button).click()

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
