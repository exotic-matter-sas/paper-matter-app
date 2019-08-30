from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv


class ManageFolderPage(BasePage):
    url = '/app/#/folders'

    breadcrumb = '.breadcrumb'

    main_loader = '.left-panel .spinner-border'

    folders_list = '.folder'
    folders_icons = '.folder .icon'
    folders_title = '.folder label'
    create_folder_button = '#create-folder'

    right_panel = '#right-panel'
    right_panel_loader = '#right-panel .spinner-border'

    selected_folder_name = '#selected-folder-name'
    rename_selected_folder_button = '#rename-selected-folder'
    move_selected_folder_button = '#move-selected-folder'
    delete_selected_folder_button = '#delete-selected-folder'

    # Move folder modal
    modal_move_folder = '#modal-move-folder'
    modal_move_folder_target_list = '.target-folder-name'

    def visit(self, url, absolute_url=False):
        super().visit(url, absolute_url)
        self.wait_folder_list_loaded()

    def wait_folder_list_loaded(self):
        self.wait_for_elem_to_disappear(self.main_loader)

    def wait_for_folder_selected(self):
        self.wait_for_elem_to_disappear(self.right_panel_loader)

    def create_folder(self, folder_name=tv.FOLDER1_NAME):
        self.get_elem(self.create_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.get_elem(self.modal_accept_button).click()
        self.wait_folder_list_loaded()

    def navigate_to_folder(self, folder_name):
        folder_list = self.get_elems(self.folders_list)
        for folder in folder_list:
            if folder.text == folder_name:
                folder.find_element_by_css_selector(self.folders_icons).click()
                self.wait_folder_list_loaded()
                break

    def select_folder(self, folder_name):
        folder_list = self.get_elems(self.folders_list)
        for folder in folder_list:
            if folder.text == folder_name:
                folder.find_element_by_css_selector(self.folders_title).click()
                self.wait_for_folder_selected()
                return folder

    def rename_selected_folder(self, folder_name):
        self.get_elem(self.rename_selected_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.get_elem(self.modal_accept_button).click()

    def move_selected_folder(self, target_folder_name):
        self.get_elem(self.move_selected_folder_button).click()
        self.wait_for_elem_to_show(self.modal_move_folder)

        target_list = self.get_elems(self.modal_move_folder_target_list)
        for target in target_list:
            if target.text.strip() == target_folder_name:
                target.click()
                break

        self.get_elem(self.modal_accept_button).click()
        self.wait_folder_list_loaded()

    def delete_selected_folder(self):
        selected_folder_name = self.get_elem_text(self.selected_folder_name)

        self.get_elem(self.delete_selected_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)

        self.get_elem(self.modal_input).send_keys(selected_folder_name)
        self.get_elem(self.modal_accept_button).click()
        self.wait_folder_list_loaded()
