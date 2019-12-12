#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage


class DocumentViewerModal(BasePage):
    url = '/app/#/home?doc={}'

    page_body = '#document-viewer'
    document_title = '#document-viewer .modal-title'

    rename_document_button = '#rename-document'
    close_document_button = '#document-viewer .close'
    move_document_button = '#move-document'
    delete_document_button = '#delete-document'

    edit_note_button = '#edit-note'
    note_textarea = '#note-textarea'
    note_text = '#note'
    save_note_button = '#save-note'

    pdf_viewer_iframe = '#document-viewer iframe'
    document_viewer_panel = '#document-viewer'

    def rename_document(self, document_name):
        self.wait_for_elem_to_show(self.rename_document_button)
        self.get_elem(self.rename_document_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(document_name)
        self.accept_modal()

    def close_document(self):
        self.get_elem(self.close_document_button).click()
        self.wait_for_elem_to_disappear(self.page_body)

    def annotate_document(self, note):
        self.get_elem(self.edit_note_button).click()
        self.wait_for_elem_to_show(self.note_textarea)
        self.get_elem(self.note_textarea).clear()
        self.get_elem(self.note_textarea).send_keys(note)
        self.get_elem(self.save_note_button).click()

    def delete_document(self):
        self.get_elem(self.delete_document_button).click()
        self.accept_modal()
        self.wait_for_elem_to_disappear(self.page_body)
