from django.test import TestCase

from ftests.tools.setup_helpers import setup_org, setup_user
from .forms import FTLUserCreationForm


class FtlUserCreationFormTests(TestCase):

    def setUp(self):
        self.org = setup_org()
        self.user = setup_user(self.org)

    def test_form_render_email_input(self):
        form = FTLUserCreationForm()
        self.assertIn('Email address', form.as_p())

    def test_form_refused_blank_email(self):
        # TODO
        pass

    def test_form_refused_duplicate_email(self):
        # TODO
        pass

    def test_form_refused_duplicate_username(self):
        # TODO
        pass
