#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import uuid
from unittest import mock
from unittest.mock import Mock, patch, call, MagicMock

import requests
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings
from jose import jwt
from langid.langid import LanguageIdentifier
from tika import parser

from core.errors import PluginUnsupportedStorage
from core.models import FTLDocument
from core.processing import ftl_processing
from core.processing.ftl_processing import (
    FTLDocumentProcessing,
    FTLDocProcessingBase,
    FTLOCRBase,
    atomic_ftl_doc_update,
)
from core.processing.proc_lang import FTLLangDetectorLangId
from core.processing.proc_ocrmypdf import FTLOCRmyPDF
from core.processing.proc_pgsql_tsvector import (
    FTLSearchEnginePgSQLTSVector,
    SEARCH_VECTOR,
)
from core.processing.proc_thumb_only_office import FTLThumbnailGenerationOnlyOffice
from core.processing.proc_tika import FTLTextExtractionTika
from core.serializers import FTLDocumentDetailsOnlyOfficeSerializer
from core.signals import pre_ftl_processing


class ProcTest(FTLDocProcessingBase):
    """
    Mocked test processing class
    """

    supported_documents_types = ["*"]

    def process(self, ftl_doc, force):
        pass


class DocumentProcessingTests(TestCase):
    def setUp(self):
        configured_plugins = ["core.test_processing.ProcTest"]
        self.processing = FTLDocumentProcessing(configured_plugins)

    def test_plugins_loading(self):
        self.assertIsNotNone(self.processing.plugins)
        instance = self.processing.plugins[0]
        self.assertTrue(isinstance(instance, (ProcTest, FTLDocProcessingBase)))

    @patch.object(FTLDocumentProcessing, "_handle")
    def test_apply_processing(self, mocked_handle):
        doc = Mock()
        self.processing.apply_processing(doc)

        mocked_handle.assert_called_once_with(doc, force=False)

    def test_apply_processing_force_boolean(self):
        mock_plugin_1 = Mock()
        mock_plugin_2 = Mock()

        mock_plugin_1.supported_documents_types = ["*"]
        mock_plugin_2.supported_documents_types = ["*"]

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)

        doc = Mock()
        self.processing.apply_processing(doc, True)

        mock_plugin_1.process.assert_called_once_with(doc, True)
        mock_plugin_2.process.assert_called_once_with(doc, True)

    def test_apply_processing_force_list(self):
        mock_plugin_1 = Mock()
        mock_plugin_2 = Mock(spec=ProcTest)

        mock_plugin_1.supported_documents_types = ["*"]
        mock_plugin_2.supported_documents_types = ["*"]

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)

        doc = Mock()
        self.processing.apply_processing(
            doc,
            [
                ".".join(
                    [
                        mock_plugin_2.__class__.__module__,
                        mock_plugin_2.__class__.__qualname__,
                    ]
                ),
            ],
        )

        mock_plugin_1.process.assert_called_once_with(doc, False)
        mock_plugin_2.process.assert_called_once_with(doc, True)

    def test_handle(self):
        mock_plugin_1 = Mock()
        mock_plugin_2 = Mock()
        mock_plugin_3 = Mock()

        mock_plugin_1.supported_documents_types = ["*"]
        mock_plugin_2.supported_documents_types = ["*"]
        mock_plugin_3.supported_documents_types = ["*"]

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)
        self.processing.plugins.append(mock_plugin_3)

        doc = Mock()
        self.processing.apply_processing(doc)

        mock_plugin_1.process.assert_called_once_with(doc, False)
        mock_plugin_2.process.assert_called_once_with(doc, False)
        mock_plugin_3.process.assert_called_once_with(doc, False)

    def test_handle_error_handling(self):
        # Given
        mocked_plugin_1 = Mock()
        mocked_plugin_1.__class__.__name__ = "Boum!"
        mocked_plugin_1.process.side_effect = Exception(
            mocked_plugin_1.__class__.__name__
        )
        mocked_plugin_2 = Mock()
        mocked_plugin_2.__class__.__name__ = "OK"
        mocked_plugin_3 = Mock()
        mocked_plugin_3.__class__.__name__ = "Badaboum!"
        mocked_plugin_3.process.side_effect = Exception(
            mocked_plugin_3.__class__.__name__
        )

        mocked_plugin_1.supported_documents_types = ["*"]
        mocked_plugin_2.supported_documents_types = ["*"]
        mocked_plugin_3.supported_documents_types = ["*"]

        self.processing.plugins = [mocked_plugin_1, mocked_plugin_2, mocked_plugin_3]
        mocked_doc = Mock()

        # When
        logger_name = ftl_processing.logger.name
        with self.assertLogs(logger_name, "ERROR") as error_logs:
            self.processing.apply_processing(mocked_doc)

        # Then
        self.assertEqual(len(error_logs.output), 3)
        self.assertIn(mocked_plugin_1.__class__.__name__, error_logs.output[0])
        self.assertNotIn(mocked_plugin_2.__class__.__name__, error_logs.output[1])
        self.assertIn(mocked_plugin_3.__class__.__name__, error_logs.output[1])

    def test_supported_type(self):
        mock_plugin_1 = Mock()
        mock_plugin_2 = Mock()
        mock_plugin_3 = Mock()

        mock_plugin_1.supported_documents_types = ["application/pdf"]
        mock_plugin_2.supported_documents_types = ["*"]
        mock_plugin_3.supported_documents_types = ["text/plain"]

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)
        self.processing.plugins.append(mock_plugin_3)

        doc1 = Mock()
        doc1.type = "application/pdf"
        self.processing.apply_processing(doc1)

        doc2 = Mock()
        doc2.type = "text/plain"
        self.processing.apply_processing(doc2)

        mock_plugin_1.process.assert_has_calls([call(doc1, False)])
        mock_plugin_2.process.assert_has_calls([call(doc1, False), call(doc2, False)])
        mock_plugin_3.process.assert_has_calls([call(doc2, False)])

    @patch.object(pre_ftl_processing, "send")
    def test_process_signal_sent(self, mocked_signal):
        doc = Mock()
        self.processing.apply_processing(doc)
        mocked_signal.assert_called_once_with(sender=ProcTest, document=doc)


class ProcLangTests(TestCase):
    @patch.object(FTLDocument, "objects")
    @patch.object(LanguageIdentifier, "from_modelstring")
    def test_process(self, mocked_from_modelstring, mocked_select_ftl_doc):
        lang = FTLLangDetectorLangId()
        mocked_classify = lang.identifier.classify
        mocked_classify.return_value = ("fr", 1.0)

        doc = Mock()
        mocked_select_ftl_doc.select_for_update().get.return_value = doc

        lang.process(doc, True)

        mocked_classify.assert_called_once_with(doc.content_text)
        self.assertEqual("french", doc.language)
        doc.save.assert_called_once()

    @patch.object(FTLDocument, "objects")
    @patch.object(LanguageIdentifier, "from_modelstring")
    def test_process_unsupported_lang(
        self, mocked_from_modelstring, mocked_select_ftl_doc
    ):
        lang = FTLLangDetectorLangId()
        mocked_classify = lang.identifier.classify
        mocked_classify.return_value = ("zz", 1.0)

        doc = Mock()
        mocked_select_ftl_doc.select_for_update().get.return_value = doc
        lang.process(doc, True)

        mocked_classify.assert_called_once_with(doc.content_text)
        doc.save.assert_called_once()

    @patch.object(FTLDocument, "objects")
    @patch.object(LanguageIdentifier, "from_modelstring")
    def test_process_langid_confidence_too_low(
        self, mocked_from_modelstring, mocked_select_ftl_doc
    ):
        lang = FTLLangDetectorLangId()
        mocked_classify = lang.identifier.classify
        mocked_classify.return_value = ("en", 0.1)

        doc = Mock()
        mocked_select_ftl_doc.select_for_update().get.return_value = doc
        lang.process(doc, True)

        mocked_classify.assert_called_once_with(doc.content_text)
        doc.save.assert_called_once()

    @patch.object(LanguageIdentifier, "from_modelstring")
    def test_process_value_exists(self, mocked_from_modelstring):
        lang = FTLLangDetectorLangId()
        mocked_classify = lang.identifier.classify

        doc = Mock()
        doc.language = "french"
        lang.process(doc, False)

        mocked_classify.assert_not_called()
        doc.save.assert_not_called()


class ProcTikaTests(TestCase):
    @patch.object(FTLDocument, "objects")
    @patch.object(parser, "from_buffer")
    def test_process(self, mocked_from_buffer, mocked_select_ftl_doc):
        doc = Mock()
        doc.binary = Mock()
        doc.binary.open.return_value.__enter__ = Mock()
        doc.binary.open.return_value.__exit__ = Mock()
        mocked_select_ftl_doc.select_for_update().get.return_value = doc

        indexed_text = {"content": "indexed text", "metadata": {"xmpTPg:NPages": 42}}
        mocked_from_buffer.return_value = indexed_text

        tika = FTLTextExtractionTika()
        tika.process(doc, True)

        mocked_from_buffer.assert_called_once()
        self.assertEqual(doc.content_text, indexed_text["content"])
        self.assertEqual(doc.count_pages, indexed_text["metadata"]["xmpTPg:NPages"])
        doc.save.assert_called()
        self.assertEqual(doc.save.call_count, 2)

    @patch.object(parser, "from_buffer")
    def test_process_value_exists(self, mocked_from_buffer):
        tika = FTLTextExtractionTika()
        doc = Mock()
        doc.content_text = "indexed text"
        doc.count_pages = 42
        tika.process(doc, False)

        mocked_from_buffer.assert_not_called()
        doc.save.assert_not_called()


class ProcPGsqlTests(TestCase):
    @patch.object(FTLDocument, "objects")
    def test_process(self, mocked_select_ftl_doc):
        pgsql = FTLSearchEnginePgSQLTSVector()
        doc = Mock()
        doc.tsvector = None
        mocked_select_ftl_doc.select_for_update().get.return_value = doc
        pgsql.process(doc, False)

        self.assertEqual(doc.tsvector, SEARCH_VECTOR)
        doc.save.assert_called_once()

    @patch.object(FTLDocument, "objects")
    def test_process_without_lang(self, mocked_select_ftl_doc):
        pgsql = FTLSearchEnginePgSQLTSVector()
        doc = Mock()
        doc.tsvector = None
        doc.language = None
        mocked_select_ftl_doc.select_for_update().get.return_value = doc
        pgsql.process(doc, False)

        self.assertEqual(doc.tsvector, SEARCH_VECTOR)
        doc.save.assert_called_once()


@override_settings(FTL_ENABLE_ONLY_OFFICE=True)
@override_settings(FTL_ONLY_OFFICE_PUBLIC_JS_URL="http://example.org/oo.js")
@override_settings(FTL_ONLY_OFFICE_API_SERVER_URL="http://example-api.org")
@override_settings(
    FTL_ONLY_OFFICE_INTERNAL_DOWNLOAD_SERVER_URL="http://example-download.org"
)
@override_settings(FTL_ONLY_OFFICE_SECRET_KEY="test_secret")
class ProcOnlyOfficeTests(TestCase):
    @patch.object(ftl_processing, "atomic_ftl_doc_update")
    @patch.object(requests, "get")
    @patch.object(requests, "post")
    @patch.object(jwt, "encode")
    @patch.object(FTLDocumentDetailsOnlyOfficeSerializer, "get_download_url_temp")
    @patch.object(FTLDocument, "objects")
    def test_process(
        self,
        mock_ftl_doc_update,
        mock_get_download_url_temp,
        mock_jwt_encode,
        mock_requests_post,
        mock_requests_get,
        mock_atomic_ftl_doc_update,
    ):
        only_office = FTLThumbnailGenerationOnlyOffice()

        doc = Mock()
        doc.pid = "test-pid"
        doc.type = "application/msword"
        doc.thumbnail_binary = None
        mock_ftl_doc_update.select_for_update().get.return_value = doc

        mock_get_download_url_temp.return_value = (
            "http://example-download.org/title.doc"
        )

        mock_jwt_encode.return_value = "jwt.token.encoded"

        # Mocked OnlyOffice conversion server response
        requests_post_response = Mock()
        requests_post_response.status_code = 200
        requests_post_response.json.return_value = {
            "fileUrl": "http://example-oo.org/thumb.png"
        }
        mock_requests_post.return_value = requests_post_response

        # Mocked thumb data
        requests_get_response = MagicMock()
        requests_get_response.iter_content.__iter__.return_value = ["1", "2"]
        mock_requests_get.return_value.__enter__ = requests_get_response

        only_office.process(doc, False)

        # Tests
        expected_only_office_config = {
            "async": False,
            "filetype": "doc",
            "key": "test-pid",
            "outputtype": "png",
            "title": "thumbnail",
            "thumbnail": {"first": True, "aspect": 2},
            "url": "http://example-download.org/title.doc",
        }

        # JWT signing called
        mock_jwt_encode.assert_called_once_with(
            expected_only_office_config, "test_secret", algorithm="HS256"
        )

        # API call to OnlyOffice conversion server
        mock_requests_post.assert_called_once_with(
            "http://example-api.org/ConvertService.ashx",
            json=expected_only_office_config,
            headers={
                "Authorization": f"Bearer jwt.token.encoded",
                "Accept": "application/json",
            },
        )

        # Download thumbnail
        requests_post_response.json.assert_called()
        mock_requests_get.assert_called_once_with(
            "http://example-oo.org/thumb.png", stream=True
        )

        # Custom partial matcher
        class AnyFile(File):
            def __eq__(self, other):
                return isinstance(other, File) and other.name == "thumb.png"

        # Doc updated with new thumbnail
        mock_atomic_ftl_doc_update.assert_called_once_with(
            "test-pid", {"thumbnail_binary": AnyFile(mock.ANY, "thumb.png")}
        )


class FTLOCRBaseTests(TestCase):
    @patch.object(FTLDocument, "objects")
    @patch.object(FTLOCRBase, "_extract_text")
    def test_process(self, mocked_extract_text, mocked_select_ftl_doc):
        expected_extracted_text = "bingo!"
        mocked_extract_text.return_value = expected_extracted_text
        base_ocr = FTLOCRBase()
        base_ocr.supported_storages.append(settings.DEFAULT_FILE_STORAGE)

        # When doc do not have a content text
        mocked_doc = Mock()
        mocked_doc.content_text = ""
        mocked_doc.ocrized = False

        mocked_select_ftl_doc.select_for_update().get.return_value = mocked_doc

        base_ocr.process(mocked_doc, False)

        # Then OCR _extract_text method is called
        mocked_extract_text.assert_called_once()
        self.assertEqual(mocked_doc.content_text, expected_extracted_text)
        mocked_doc.save.assert_called_once()

        # When doc already have a content text
        mocked_extract_text.reset_mock()
        original_doc_content = ":)"
        mocked_doc = Mock()
        mocked_doc.content_text = original_doc_content

        base_ocr.process(mocked_doc, False)

        # Then OCR _extract_text method is skipped
        mocked_extract_text.assert_not_called()
        self.assertEqual(mocked_doc.content_text, original_doc_content)
        mocked_doc.save.assert_not_called()

    @patch.object(FTLOCRBase, "_extract_text")
    def test_process_with_invalid_storage(self, mocked_extract_text):
        base_ocr = FTLOCRBase()

        # When DEFAULT_FILE_STORAGE does not match supported storages
        base_ocr.supported_storages.append("this.is.not.the.default.storage")
        mocked_doc = Mock()
        mocked_doc.content_text = ""

        # Then PluginUnsupportedStorage is raised
        with self.assertRaises(PluginUnsupportedStorage):
            base_ocr.process(mocked_doc, False)

    @patch.object(FTLDocument, "objects")
    def test_atomic_ftl_doc_update(self, mocked_select_ftl_doc):
        uuid_ = uuid.uuid4()
        doc = Mock()
        doc.pid = uuid_
        doc.field_1 = 123
        doc.field_2 = "Test"
        doc.field_3 = False
        mocked_select_ftl_doc.select_for_update().get.return_value = doc

        atomic_ftl_doc_update(
            uuid_,
            {"field_1": 456, "field_2": "NoTest", "field_3": True, "field_4": 12.4},
        )

        self.assertEqual(doc.field_1, 456)
        self.assertEqual(doc.field_2, "NoTest")
        self.assertEqual(doc.field_3, True)
        self.assertEqual(doc.field_4, 12.4)
        mocked_select_ftl_doc.select_for_update().get.assert_called_once_with(pid=uuid_)
        doc.save.assert_called_once_with(
            update_fields=["field_1", "field_2", "field_3", "field_4"]
        )


class ProcOCRMyPDFTests(TestCase):
    @patch.object(requests, "get")
    @patch.object(requests, "post")
    def test_process(
        self, mock_requests_post, mock_requests_get,
    ):
        proc = FTLOCRmyPDF("http://ocrmypdf-api.example.org", "secret-api-key")

        doc = Mock()
        doc.binary = Mock()

        # Mock upload to OCR API
        requests_post_response = Mock()
        requests_post_response.status_code = 200
        requests_post_response.json.return_value = {
            "pid": "test-pid",
            "status": "received",
        }
        mock_requests_post.return_value = requests_post_response

        # Mock get API response
        requests_get_response = MagicMock()
        requests_get_response.status_code = 200
        requests_get_response.json.side_effect = [
            {"pid": "test-pid", "status": "received"},
            {"pid": "test-pid", "status": "processing"},
            {"pid": "test-pid", "status": "done"},
            {"pid": "test-pid", "status": "done"},
        ]
        requests_get_response.content = "OCR TEXT DATA"
        mock_requests_get.return_value = requests_get_response

        text = proc._extract_text(doc.binary)

        # Tests
        self.assertEqual(text, "OCR TEXT DATA")

        mock_requests_post.assert_called_once_with(
            "http://ocrmypdf-api.example.org/ocr",
            params={"lang": ["eng", "fra"]},
            files={"file": doc.binary},
            headers={"X-API-KEY": "secret-api-key"},
        )

        mock_requests_get.assert_any_call(
            "http://ocrmypdf-api.example.org/ocr/test-pid",
            headers={"X-API-KEY": "secret-api-key"},
        )

        mock_requests_get.assert_any_call(
            "http://ocrmypdf-api.example.org/ocr/test-pid/txt",
            headers={"X-API-KEY": "secret-api-key"},
        )
