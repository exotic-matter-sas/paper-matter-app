from selenium.common.exceptions import NoSuchElementException

from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftests.tools import test_values as tv


class HomePageTests(LoginPage, HomePage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    def test_upload_document_to_root(self):
        # User upload a document
        self.upload_document()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem(self.first_document_title).text)

    def test_upload_document_to_subfolder(self):
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
        self.assertRaises(NoSuchElementException)

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

        # The folder properly appears inn the folder list
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
        pass  # TODO
