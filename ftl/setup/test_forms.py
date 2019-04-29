from django.test import TestCase

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_user
from .forms import AdminCreationForm


class FtlAdminCreationFormTests(TestCase):

    def setUp(self):
        self.org = setup_org()

    def test_form_render_email_input(self):
        """Form render email input"""
        form = AdminCreationForm()
        self.assertIn('Email address', form.as_p())

    def test_form_refuse_blank_email(self):
        """Form refuse blank email"""
        form = AdminCreationForm(data={
            'username': tv.USER1_USERNAME,
            'email': '',
            'password1': tv.USER1_PASS,
            'password2': tv.USER1_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_refuse_non_unique_email(self):
        """Form refuse non unique email"""
        setup_user(self.org, username=tv.USER1_USERNAME, email=tv.USER1_EMAIL)

        form = AdminCreationForm(data={
            'username': tv.USER2_USERNAME,
            'email': tv.USER1_EMAIL,
            'password1': tv.USER2_PASS,
            'password2': tv.USER2_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_refuse_non_unique_username(self):
        """Form refuse non unique username"""
        setup_user(self.org, username=tv.USER1_USERNAME, email=tv.USER1_EMAIL)

        form = AdminCreationForm(data={
            'username': tv.USER1_USERNAME,
            'email': tv.USER2_EMAIL,
            'password1': tv.USER2_PASS,
            'password2': tv.USER2_PASS,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_admin_creation_permissions(self):
        form = AdminCreationForm(data={
            'username': tv.ADMIN_USERNAME,
            'email': tv.ADMIN_EMAIL,
            'password1': tv.ADMIN_PASS,
            'password2': tv.ADMIN_PASS,
        })

        user = form.save()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
