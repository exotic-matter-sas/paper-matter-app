from ftests.pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = '/app/'

        self.profile_name = '#username'
        self.refresh_documents_button = '#refresh-documents'

        self.first_document_title = '.document-title span'

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()
