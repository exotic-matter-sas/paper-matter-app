#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage


class MoveDocumentsModal(BasePage):
    move_document_modal = "[id^='modal-move-document']"
    move_documents_modal = "[id^='modal-move-document']"
    move_document_target_list = ".target-folder-name"

    def move_document(self, target_folder_name):
        self.wait_for_elem_to_show(self.move_document_modal)
        self._select_target(target_folder_name)
        self.accept_modal()

    def move_documents(self, target_folder_name):
        self.wait_for_elem_to_show(self.move_documents_modal)
        self._select_target(target_folder_name)
        self.accept_modal()

    def _select_target(self, target_folder_name):
        target_list = self.get_elems(self.move_document_target_list)
        for target in target_list:
            if target.text.strip() == target_folder_name:
                target.click()
                break
