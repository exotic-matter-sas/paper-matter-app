from ftests.pages.base_page import BasePage


class DocumentViewPage(BasePage):
    url = '/app/#/home?doc={}'

    page_body = '.doc-view-modal'
    document_title = '#document-title'
    document_close = '#close-document'

    def close_document(self):
        self.get_elem(self.document_close).click()
        self.wait_for_elem_to_disappear(self.page_body)
