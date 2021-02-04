#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import time

from django.utils import timezone
from selenium.common.exceptions import NoSuchElementException

from ftests.pages.base_page import BasePage


class DocumentViewerModal(BasePage):
    url = "/app/#/home?doc={}"

    page_body = "#document-viewer"
    document_title = "#document-title"

    rename_document_button = "#rename-document"
    previous_document_button = "#previous-next-big button:first-child"
    next_document_button = "#previous-next-big button:last-child"
    close_document_button = "#document-viewer .close"
    download_button = "#download-document"
    download_button_dropdown = "#download-document .dropdown-toggle"
    open_pdf_button = "#open-document"
    move_document_button = "#move-document"
    delete_document_button = "#delete-document"
    document_reminder_button = "#document-reminder"

    edit_note_button = "#edit-note"
    note_textarea = "#note-textarea"
    note_text = "#note"
    save_note_button = "#save-note"

    pdf_viewer_iframe = "#pdf-embed-container iframe"
    document_viewer_panel = "#document-viewer"
    compatibility_viewer_button = "label[for='toggle-compat-viewer']"
    pdf_native_viewer = "#pdf-embed-container embed"

    share_document_button = "#share-document"
    validate_modal_button = "#"
    unshare_modal_button = "[id^='modal-document-sharing'] .modal-footer .btn-danger"

    reminder_for_tomorrow_button = (
        ".b-calendar .b-calendar-inner > footer .btn:first-child"
    )
    reminder_add_reminder_button = ".modal-content footer button.btn-primary"
    reminder_list_elements = ".list-group .list-group-item"
    reminder_list_elements_date = ".list-group .list-group-item h5 span"
    reminder_list_elements_note = ".list-group .list-group-item div:nth-child(2)"
    reminder_list_elements_delete = ".list-group .list-group-item button"
    reminder_list_empty = "[id^=modal-document-reminder] .align-items-center span"
    reminder_note_input = "#reminder-note"
    reminder_close_button = "[id^=modal-document-reminder] .close"

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
        try:
            self.get_elem(self.edit_note_button).click()
        except NoSuchElementException:
            pass
        self.wait_for_elem_to_show(self.note_textarea)
        self.get_elem(self.note_textarea).clear()
        self.get_elem(self.note_textarea).send_keys(note)
        self.get_elem(self.save_note_button).click()

    def delete_document(self):
        self.get_elem(self.delete_document_button).click()
        self.accept_modal()
        self.wait_for_elem_to_disappear(self.page_body)

    def share_document(self):
        self.wait_for_elem_to_show(self.share_document_button)
        self.get_elem(self.share_document_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.wait_for_elem_text_not_to_be(self.modal_input, "")
        link = self.get_elem_text(self.modal_input)
        return link

    def unshare_document(self):
        self.wait_for_elem_to_show(self.share_document_button)
        self.get_elem(self.share_document_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.wait_for_elem_text_not_to_be(self.modal_input, "")
        self.get_elem(self.unshare_modal_button).click()

    def add_document_reminder_tomorrow(self, note=""):
        self.wait_for_elem_to_show(self.document_reminder_button)
        self.get_elem(self.document_reminder_button).click()
        self.wait_for_elem_to_show(self.reminder_add_reminder_button)
        self.get_elem(self.reminder_for_tomorrow_button).click()
        self.get_elem(self.reminder_note_input).send_keys(note)
        self.get_elem(self.reminder_add_reminder_button).click()
        self.wait_for_elem_to_show(self.reminder_list_elements)
        self.get_elem(self.reminder_close_button).click()

    def delete_document_reminder(self, alert_date=timezone.now()):
        self.wait_for_elem_to_show(self.document_reminder_button)
        self.get_elem(self.document_reminder_button).click()
        self.wait_for_elem_to_show(self.reminder_add_reminder_button)

        reminders = self.get_elems(self.reminder_list_elements_date)
        reminder_index_to_delete = 100
        for i, reminder in enumerate(reminders):
            if alert_date.date().isoformat() in reminder.get_attribute("title"):
                reminder_index_to_delete = i
                break

        reminders_delete = self.get_elems(self.reminder_list_elements_delete)
        if len(reminders_delete) > reminder_index_to_delete:
            reminders_delete[reminder_index_to_delete].click()
        time.sleep(0.5)
