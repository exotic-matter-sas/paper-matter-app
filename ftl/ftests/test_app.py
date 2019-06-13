from unittest import skip, skipIf
from unittest.mock import patch

from selenium.common.exceptions import NoSuchElementException
from tika import parser

from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftl.settings import DEV_MODE


class HomePageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(parser, 'from_file')
    def test_upload_document_to_root(self, mock_tika_parser):
        mock_tika_parser.return_value = ""

        # User upload a document
        self.upload_document()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem(self.first_document_title).text)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
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

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
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

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder(self):
        # User create a folder
        self.create_folder()

        # The folder properly appears in the folder list
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem(self.first_folder_button).text)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
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
        self.wait_for_element_to_show(self.first_folder_button)
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.wait_for_element_to_show(self.first_folder_button)
        self.assertEqual(tv.FOLDER2_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.wait_for_element_to_show(self.first_folder_button)
        self.assertEqual(tv.FOLDER3_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()

    @skip('TODO when implemented in UI')  # TODO
    def test_delete_folder(self):
        pass

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_document_by_its_title(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        setup_document(self.org, self.user, title=second_document_title)

        # User search last uploaded document
        self.search_document(second_document_title)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_list)), 1)
        self.assertEqual(second_document_title, self.get_elem(self.first_document_title).text)

    @skip('TODO when document note implemented in UI')  # TODO
    def test_search_document_by_its_note(self):
        pass

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_document_by_its_content(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        second_document_text_content = 'Yellow Blue'
        setup_document(self.org, self.user, title=second_document_title, text_content=second_document_text_content)

        # User search last uploaded document
        self.search_document(second_document_text_content)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_list)), 1)
        self.assertEqual(second_document_title, self.get_elem(self.first_document_title).text)
