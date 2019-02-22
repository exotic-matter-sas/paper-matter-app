import platform
import os
import unittest

from selenium import webdriver

from ftl.ftl.settings import BASE_DIR


class LandingPageTest(unittest.TestCase):

    def setUp(self):
        if platform.system().startswith('Linux'):
            executable_path = 'functional_tests/geckodriver/geckodriver64_linux'
        elif platform.system().startswith('Windows'):
            executable_path = 'functional_tests/geckodriver/geckodriver64.exe'
        elif platform.system().startswith('Darwin'):
            executable_path = 'functional_tests/geckodriver/geckodriver64_linux'
        else:
            raise EnvironmentError(f'Platform "{platform.system()}" not supported')

        self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path))

    def tearDown(self):
        self.browser.quit()

    def test_landing_page_display_properly_on_first_visit(self):
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get('http://localhost:8000')

        # A landing page welcome the user and ask him to set admin information
        self.assertIn('Ftl-app', self.browser.title)
        self.fail('Finish the test !')

        # He fulfill the admin creation form (and first organisation ?)

        # A success page mention the urls for admin login page and user signin page

        # Display ftl-app again now redirect to user signin page


if __name__ == '__main__':
    unittest.main()
