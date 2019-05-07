import os

from ftl.settings import BASE_DIR
from ftests.pages.base_page import BasePage


class HomePage(BasePage):
    url = '/app/'

    profile_name = '#username'
    document_upload_input = 'input[type="file"]'
    submit_document_upload_button = '#upload-button'
    refresh_documents_button = '#refresh-documents'

    first_document_title = '.document-title span'

    def upload_document(self, path=None):
        if not path:
            path = os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf')
        self.get_elem(self.document_upload_input).send_keys(path)
        self.get_elem(self.submit_document_upload_button).click()

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()
