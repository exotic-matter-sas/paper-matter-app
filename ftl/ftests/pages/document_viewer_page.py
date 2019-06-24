from ftests.pages.base_page import BasePage


class DocumentViewPage(BasePage):
    url = '/app/#/home?doc={}'

    page_body = '#document-viewer'
    document_title = '#document-viewer .modal-title'
    document_close = '#document-viewer .close'

    pdf_viewer = '#document-viewer iframe'

    def close_document(self):
        self.get_elem(self.document_close).click()
        self.wait_for_elem_to_disappear(self.page_body)
