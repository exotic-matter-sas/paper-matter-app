from ftests.pages.base_page import BasePage


class HomePage(BasePage):
    url = '/app/'

    profile_name = '#username'
    refresh_documents_button = '#refresh-documents'

    first_document_title = '.document-title span'

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()
