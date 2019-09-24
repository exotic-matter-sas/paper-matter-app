from ftests.pages.base_page import BasePage


class MoveDocumentsModal(BasePage):
    move_document_modal = '#modal-move-documents'
    move_document_target_list = '.target-folder-name'

    def move_documents(self, target_folder_name):
        self.wait_for_elem_to_show(self.move_document_modal)

        target_list = self.get_elems(self.move_document_target_list)
        for target in target_list:
            if target.text.strip() == target_folder_name:
                target.click()
                break

        self.get_elem(self.modal_accept_button).click()
