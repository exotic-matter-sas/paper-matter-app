import os
import time
from unittest.mock import patch

from selenium.common.exceptions import NoSuchElementException
from tika import parser

from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftl.settings import BASE_DIR


class HomePageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @patch.object(parser, 'from_file')
    def test_upload_document_to_root(self, mock_tika_parser):
        mock_tika_parser.return_value = ""

        # User upload a document
        self.upload_document()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem(self.first_document_title).text)

    @patch.object(parser, 'from_file')
    def test_upload_document_to_subfolder(self, mock_tika_parser):
        mock_tika_parser.return_value = ""

        # User has already created a folder
        setup_folder(self.org)
        self.visit(HomePage.url)

        # User upload open its subfolder and upload a document
        self.get_elem(self.first_folder_button).click()
        self.upload_document()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem(self.first_document_title).text)
        # Document doesn't appears in root folder
        self.visit(HomePage.url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.first_document_title)

    def test_display_document(self):
        # User has already added a document
        setup_document(self.org, self.user)
        self.refresh_document_list()

        # User click on the first listed document
        self.open_first_document()
        # User can see the pdf inside the pdf viewer
        pdf_viewer_iframe = self.browser.find_element_by_css_selector('.doc-view-modal iframe')
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.browser.find_element_by_css_selector('title').get_attribute("innerHTML")

        self.assertEqual(pdf_viewer_iframe_title, 'PDF.js viewer')

    def test_create_folder(self):
        # User create a folder
        self.create_folder()

        # The folder properly appears in the folder list
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem(self.first_folder_button).text)

    def test_create_folder_tree(self):
        # User create a folder at root level
        self.create_folder(tv.FOLDER1_NAME)
        # User open previous folder and create a subfolder
        self.get_elem(self.first_folder_button).click()
        self.create_folder(tv.FOLDER2_NAME)
        # User open previous folder and create another subfolder
        self.get_elem(self.first_folder_button).click()
        self.create_folder(tv.FOLDER3_NAME)

        # Check if each folder have been created at proper level
        self.visit(HomePage.url)
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.assertEqual(tv.FOLDER2_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.assertEqual(tv.FOLDER3_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()

    def test_delete_folder(self):
        pass  # TODO when implemented in UI

    def test_search_document_by_its_title(self):
        # User add 2 documents
        self.upload_document(os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf'))
        second_document_name = 'green.pdf'
        self.upload_document(os.path.join(BASE_DIR, 'ftests', 'tools', second_document_name))
        # User wait document indexation
        time.sleep(5)  # TODO replace by a wait_for type of call when a indexation indicator will be available

        # User search last uploaded document
        self.search_document(second_document_name)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems('.document-thumbnail')), 1)
        self.assertEqual(second_document_name, self.get_elem(self.first_document_title).text)

    def test_search_document_by_its_note(self):
        pass  # TODO when note implemented in UI

    def test_search_document_by_its_content(self):
        # User add 2 documents
        self.upload_document(os.path.join(BASE_DIR, 'ftests', 'tools', 'test.pdf'))
        second_document_name = 'green.pdf'
        self.upload_document(os.path.join(BASE_DIR, 'ftests', 'tools', second_document_name))
        # User wait document indexation
        time.sleep(5)  # TODO replace by a wait_for type of call when a indexation indicator will be available

        # User search a word contain in the second document
        self.search_document('Yellow Blue')

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems('.document-thumbnail')), 1)
        self.assertEqual(second_document_name, self.get_elem(self.first_document_title).text)
