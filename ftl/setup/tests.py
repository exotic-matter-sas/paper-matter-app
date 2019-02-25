from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from .views import LandingPageView


class SetupPageTest(TestCase):

    def test_setup_url_resolve_landing_page_view(self):
        found = resolve('/setup/')
        self.assertEqual(found.func, LandingPageView.as_view())

    def test_landing_page_returns_correct_html(self):
        request = HttpRequest()
        response = LandingPageView.as_view(request)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'Landing page', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
