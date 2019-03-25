from django.test import TestCase
from django.core.exceptions import ValidationError

from ftests.tools import test_values as tv
from .models import FTLUser, FTLDocument, FTLFolder


class FTLUserModelTest(TestCase):

    def test_ftl_user_must_have_an_org(self):
        with self.assertRaises(ValidationError):
            try:
                FTLUser(username=tv.USER1_USERNAME,
                        password=tv.USER1_PASS).full_clean()
            except ValidationError as e:
                self.assertIn('org', str(e))
                raise

    def test_ftl_documents_must_have_user_and_org(self):
        with self.assertRaises(ValidationError):
            try:
                FTLDocument(title=tv.USER1_USERNAME).full_clean()
            except ValidationError as e:
                self.assertIn('user', str(e))
                self.assertIn('org', str(e))
                raise

    def test_ftl_folder_must_have_an_org(self):
        with self.assertRaises(ValidationError):
            try:
                FTLFolder(name=tv.FOLDER1_NAME).full_clean()
            except ValidationError as e:
                self.assertIn('org', str(e))
                raise
