from ftests.pages.base_page import BasePage


class DocumentViewerModal(BasePage):
    url = '/app/#/home?doc={}'

    page_body = '#document-viewer'
    document_title = '#document-viewer .modal-title'

    rename_document_button = '#rename-document'
    close_document_button = '#document-viewer .close'
    move_document_button = '#move-document'

    pdf_viewer = '#document-viewer iframe'

    def rename_document(self, document_name):
        self.wait_for_elem_to_show(self.rename_document_button)
        self.get_elem(self.rename_document_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(document_name)
        self.get_elem(self.modal_accept_button).click()

    def close_document(self):
        self.get_elem(self.close_document_button).click()
        self.wait_for_elem_to_disappear(self.page_body)
