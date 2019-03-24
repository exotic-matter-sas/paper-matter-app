from django.test import TestCase

from ftests.tools.setup_helpers import setup_org, setup_user
from .forms import FTLUserCreationForm
from ftests.tools import test_values as tv


class FtlUserCreationFormTests(TestCase):

    def setUp(self):
        self.org = setup_org()

    def test_form_render_email_input(self):
        form = FTLUserCreationForm()
        self.assertIn('Email address', form.as_p())

    def test_form_refused_blank_email(self):
        form = FTLUserCreationForm(data={
            'username': tv.USER1_USERNAME,
            'email': '',
            'password1': tv.USER1_PASS,
            'password2': tv.USER1_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_refused_duplicate_email(self):
        setup_user(self.org, username=tv.USER1_USERNAME, email=tv.USER1_EMAIL)

        form = FTLUserCreationForm(data={
            'username': tv.USER2_USERNAME,
            'email': tv.USER1_EMAIL,
            'password1': tv.USER2_PASS,
            'password2': tv.USER2_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_refused_duplicate_username(self):
        setup_user(self.org, username=tv.USER1_USERNAME, email=tv.USER1_EMAIL)

        form = FTLUserCreationForm(data={
            'username': tv.USER1_USERNAME,
            'email': tv.USER2_EMAIL,
            'password1': tv.USER2_PASS,
            'password2': tv.USER2_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
