from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from .views import landing_page


class SetupPageTest(TestCase):

    def test_setup_url_resolve_landing_page_view(self):
        found = resolve('/setup/')
        self.assertEqual(found.func, landing_page)

    def test_landing_page_returns_correct_html(self):
        request = HttpRequest()
        response = landing_page(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'Landing page', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
