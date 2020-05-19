#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import unittest
from unittest.mock import patch, Mock

import puremagic
from django.core.files.uploadedfile import SimpleUploadedFile

from core import mimes
from core.mimes import mimetype_to_ext, guess_mimetype, _uploaded_file_obj_to_buffer


class MimesTests(unittest.TestCase):
    def test_mimetype_to_ext(self):
        # FTL default type
        self.assertEqual(mimetype_to_ext("application/pdf"), ".pdf")
        self.assertEqual(mimetype_to_ext("text/plain"), ".txt")
        self.assertEqual(mimetype_to_ext("application/rtf"), ".rtf")
        self.assertEqual(mimetype_to_ext("text/rtf"), ".rtf")
        self.assertEqual(mimetype_to_ext("application/msword"), ".doc")
        self.assertEqual(mimetype_to_ext("application/vnd.ms-excel"), ".xls")
        self.assertEqual(mimetype_to_ext("application/vnd.ms-powerpoint"), ".ppt")
        self.assertEqual(
            mimetype_to_ext(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            ".docx",
        )
        self.assertEqual(
            mimetype_to_ext(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            ".xlsx",
        )
        self.assertEqual(
            mimetype_to_ext(
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            ),
            ".pptx",
        )
        self.assertEqual(
            mimetype_to_ext("application/vnd.oasis.opendocument.text"), ".odt"
        )
        self.assertEqual(
            mimetype_to_ext("application/vnd.oasis.opendocument.presentation"), ".odp"
        )
        self.assertEqual(
            mimetype_to_ext("application/vnd.oasis.opendocument.spreadsheet"), ".ods"
        )

        # Unknown type
        self.assertIsNone(mimetype_to_ext("application/octet-stream"))

    @patch.object(puremagic, "from_string")
    @patch.object(mimes, "_uploaded_file_obj_to_buffer")
    def test_guess_mimetype(
        self, mocked_uploaded_file_obj_to_buffer, mocked_from_string
    ):
        mocked_uploaded_file_obj_to_buffer.return_value = b"123", b"456"
        mocked_from_string.return_value = "mime/test"
        uploaded = Mock()

        mime = guess_mimetype(uploaded, "a_text_file.txt")

        mocked_uploaded_file_obj_to_buffer.assert_called_once_with(uploaded)
        mocked_from_string.assert_called_once_with(
            b"123456", mime=True, filename="a_text_file.txt"
        )
        self.assertEqual(mime, "mime/test")

    @patch.object(puremagic, "from_string")
    @patch.object(mimes, "_uploaded_file_obj_to_buffer")
    def test_guess_mimetype_cant_decode(
        self, mocked_uploaded_file_obj_to_buffer, mocked_from_string
    ):
        mocked_uploaded_file_obj_to_buffer.return_value = b"123", b"456"
        mocked_from_string.side_effect = puremagic.PureError("Boom!")
        uploaded = Mock()

        # should use file extension
        mime = guess_mimetype(uploaded, "a_text_file.rtf")
        self.assertEqual(mime, "application/rtf")

        # file extension is not usable
        mime = guess_mimetype(uploaded, "unknown_file")
        self.assertIsNone(mime)

    def test_uploaded_file_obj_to_buffer(self):
        uploaded = SimpleUploadedFile("filename", b"content of the file")

        # File size is smaller than sample size
        head, foot = _uploaded_file_obj_to_buffer(uploaded)
        self.assertEqual(head, b"content of the file")
        self.assertEqual(foot, b"")

        # File size is greater than sample size
        head, foot = _uploaded_file_obj_to_buffer(uploaded, sample_size=4)
        self.assertEqual(head, b"cont")
        self.assertEqual(foot, b"file")
