from unittest import skip, skipIf
from unittest.mock import patch

from selenium.common.exceptions import NoSuchElementException
from tika import parser

from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.document_viewer_page import DocumentViewPage
from ftests.pages.home_page import HomePage
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder
from ftl.settings import DEV_MODE


class HomePageTests(LoginPage, HomePage, DocumentViewPage):
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
        pdf_viewer_iframe = self.get_elem(self.pdf_viewer)
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.get_elem('title', False).get_attribute("innerHTML")

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
        self.wait_for_elem_to_show(self.first_folder_button)
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.wait_for_elem_to_show(self.first_folder_button)
        self.assertEqual(tv.FOLDER2_NAME, self.get_elem(self.first_folder_button).text)
        self.get_elem(self.first_folder_button).click()
        self.wait_for_elem_to_show(self.first_folder_button)
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
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
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
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(second_document_title, self.get_elem(self.first_document_title).text)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_not_found(self):
        # User have already added 1 document
        setup_document(self.org, self.user)

        # User search something that isn't present in his document
        self.search_document('this text doesn\'t exist')

        with self.assertRaises(NoSuchElementException, msg='No document should be found by this search query'):
            self.get_elems(self.documents_thumbnails)

        self.assertIn('No document', self.get_elem_text(self.documents_list),
                      'A message should indicate no document where found')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_search_query(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        setup_document(self.org, self.user, title=second_document_title)

        # User search last uploaded document
        self.visit(f'/app/#/home?q={second_document_title}')
        self.wait_document_list_loaded()

        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1,
                         'Only second document should appears in the search result')
        self.assertEqual(second_document_title, self.get_elem(self.first_document_title).text,
                         'Second document title should appears in search result')

        # TODO renable this test when https://gitlab.com/exotic-matter/ftl-app/issues/42 fixed
        """
        self.assertEqual(second_document_title, self.get_elem_text(self.search_input),
                         'Search input should be prefilled with search query')
        """

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_folder_id(self):
        # User already created a 3 levels folder three (a > b > c) and have added a document inside c folder
        folder_a = setup_folder(self.org)
        folder_b = setup_folder(self.org, parent=folder_a)
        folder_c = setup_folder(self.org, parent=folder_b)
        document = setup_document(self.org, self.user, folder_c, title='bingo!')

        # User open folder c through url
        self.visit(f'/app/#/home/folderFakePath/{folder_c.id}')
        self.wait_document_list_loaded()

        self.assertEqual(document.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in folder C')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_folder_navigation_using_browser_previous_and_next(self):
        # User already created a 3 levels folder three (a > b > c) and have added a document inside each of them
        # plus one at root level
        document_root = setup_document(self.org, self.user, title='document_root')
        folder_a = setup_folder(self.org)
        document_a = setup_document(self.org, self.user, folder_a, title='document_a')
        folder_b = setup_folder(self.org, parent=folder_a)
        document_b = setup_document(self.org, self.user, folder_b, title='document_b')
        folder_c = setup_folder(self.org, parent=folder_b)
        document_c = setup_document(self.org, self.user, folder_c, title='document_c')
        self.visit(HomePage.url)

        # User browse to folder c
        self.wait_document_list_loaded()
        self.get_elem(self.first_folder_button).click()
        self.wait_folder_list_loaded()
        self.get_elem(self.first_folder_button).click()
        self.wait_folder_list_loaded()
        self.get_elem(self.first_folder_button).click()
        self.wait_folder_list_loaded()

        # User use the browser previous button to come back to root
        self.previous_page()
        self.wait_document_list_loaded()
        self.assertEqual(document_b.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in folder b')
        self.previous_page()
        self.wait_document_list_loaded()
        self.assertEqual(document_a.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in folder a')
        self.previous_page()
        self.wait_document_list_loaded()
        self.assertEqual(document_root.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in root folder')
        self.next_page()
        self.wait_document_list_loaded()
        self.next_page()
        self.wait_document_list_loaded()
        self.next_page()
        self.wait_document_list_loaded()
        self.assertEqual(document_c.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in folder c')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_document_list_pagination(self):
        # User has already added 21 documents
        for i in range(21):
            setup_document(self.org, self.user, title=i+1)
        self.refresh_document_list()

        # Only 10 documents are shown by default
        self.wait_document_list_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '12')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 10)

        # User display 10 more document
        self.get_elem(self.more_documents_button).click()
        self.wait_more_documents_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '2')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 20)

        # User display the last document
        self.get_elem(self.more_documents_button).click()
        self.wait_more_documents_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '1')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 21)

        # There are no more documents to show
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.more_documents_button)


class DocumentViewPageTests(LoginPage, HomePage, DocumentViewPage):
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
    def test_visit_url_with_document_pid(self, mock_tika_parser):
        mock_tika_parser.return_value = ""
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        second_document = setup_document(self.org, self.user, title=second_document_title)

        # User open second document through url
        self.visit(DocumentViewPage.url.format(second_document.pid))
        self.wait_for_elem_to_show(self.document_title)

        self.assertIn(second_document_title,
                      self.get_elem_text(self.document_title),
                      'Setup document title should match opened document')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(parser, 'from_file')
    def test_visit_url_with_folder_id_and_document_pid(self, mock_tika_parser):
        mock_tika_parser.return_value = ""
        # User already created a 3 levels folder three (a > b > c) and have added a document inside c folder
        folder_a = setup_folder(self.org)
        folder_b = setup_folder(self.org, parent=folder_a)
        folder_c = setup_folder(self.org, parent=folder_b)
        document_title = 'bingo!'
        document = setup_document(self.org, self.user, folder_c, title=document_title)

        # User open folder and document through url
        self.visit(f'{HomePage.url}#/home/folderFakePath/{folder_c.id}?doc={document.pid}')
        self.wait_for_elem_to_show(self.document_title)

        self.assertIn(document_title,
                      self.get_elem_text(self.document_title),
                      'Setup document title should match opened document')

        self.close_last_notification()  # close thumbnail generated notification

        # User close document
        self.close_document()
        self.assertEqual(document.title, self.get_elem(self.first_document_title).text,
                         'Setup document title should appears in folder C')
