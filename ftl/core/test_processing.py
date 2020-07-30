#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import uuid
from unittest.mock import Mock, patch, call

from django.test import TestCase
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
from core.processing.proc_pgsql_tsvector import (
    FTLSearchEnginePgSQLTSVector,
    SEARCH_VECTOR,
)
from core.processing.proc_tika import FTLTextExtractionTika
from core.signals import pre_ftl_processing
from ftl.settings import DEFAULT_FILE_STORAGE


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


class FTLOCRBaseTests(TestCase):
    @patch.object(FTLDocument, "objects")
    @patch.object(FTLOCRBase, "_extract_text")
    def test_process(self, mocked_extract_text, mocked_select_ftl_doc):
        expected_extracted_text = "bingo!"
        mocked_extract_text.return_value = expected_extracted_text
        base_ocr = FTLOCRBase()
        base_ocr.supported_storages.append(DEFAULT_FILE_STORAGE)

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
