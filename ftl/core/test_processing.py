from concurrent.futures import wait as wait_futures
from unittest.mock import Mock, patch

import langid
from django.test import TestCase
from tika import parser

from core.errors import PluginUnsupportedStorage
from core.processing import ftl_processing
from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase, FTLOCRBase
from core.processing.proc_lang import FTLLangDetectorLangId
from core.processing.proc_pgsql_tsvector import FTLSearchEnginePgSQLTSVector, SEARCH_VECTOR
from core.processing.proc_tika import FTLTextExtractionTika
from ftl.settings import DEFAULT_FILE_STORAGE


class ProcTest(FTLDocProcessingBase):
    """
    Mocked test processing class
    """

    def process(self, ftl_doc):
        pass


class DocumentProcessingTests(TestCase):
    def setUp(self):
        configured_plugins = ['core.test_processing.ProcTest']
        self.processing = FTLDocumentProcessing(configured_plugins)

    def test_plugins_loading(self):
        self.assertIsNotNone(self.processing.plugins)
        instance = self.processing.plugins[0]
        self.assertTrue(isinstance(instance, (ProcTest, FTLDocProcessingBase)))

    def test_apply_processing(self):
        self.processing.executor.submit = Mock()

        doc = Mock()
        self.processing.apply_processing(doc)

        self.processing.executor.submit.assert_called_once_with(self.processing._handle, doc)

    def test_handle(self):
        mock_plugin_1 = Mock()
        mock_plugin_2 = Mock()
        mock_plugin_3 = Mock()

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)
        self.processing.plugins.append(mock_plugin_3)

        doc = Mock()
        future = self.processing.apply_processing(doc)
        wait_futures([future], timeout=10)

        mock_plugin_1.process.assert_called_once_with(doc)
        mock_plugin_2.process.assert_called_once_with(doc)
        mock_plugin_3.process.assert_called_once_with(doc)

    def test_handle_error_handling(self):
        # Given
        mocked_plugin_1 = Mock()
        mocked_plugin_1.__class__.__name__ = 'Boum!'
        mocked_plugin_1.process.side_effect = Exception(mocked_plugin_1.__class__.__name__)
        mocked_plugin_2 = Mock()
        mocked_plugin_2.__class__.__name__ = 'OK'
        mocked_plugin_3 = Mock()
        mocked_plugin_3.__class__.__name__ = 'Badaboum!'
        mocked_plugin_3.process.side_effect = Exception(mocked_plugin_3.__class__.__name__)

        self.processing.plugins = [mocked_plugin_1, mocked_plugin_2, mocked_plugin_3]
        mocked_doc = Mock()

        # When
        logger_name = ftl_processing.logger.name
        with self.assertLogs(logger_name, 'ERROR') as error_logs:
            future = self.processing.apply_processing(mocked_doc)
            wait_futures([future], timeout=10)

        # Then
        self.assertEqual(len(error_logs.output), 3)
        self.assertIn(mocked_plugin_1.__class__.__name__, error_logs.output[0])
        self.assertNotIn(mocked_plugin_2.__class__.__name__, error_logs.output[1])
        self.assertIn(mocked_plugin_3.__class__.__name__, error_logs.output[1])


class ProcLangTests(TestCase):

    @patch.object(langid, 'classify')
    def test_process(self, mocked_classify):
        mocked_classify.return_value = ['fr']

        lang = FTLLangDetectorLangId()
        doc = Mock()
        lang.process(doc)

        mocked_classify.assert_called_once_with(doc.content_text)
        self.assertEqual('french', doc.language)
        doc.save.assert_called_once()


class ProcTikaTests(TestCase):

    @patch.object(parser, 'from_buffer')
    def test_process(self, mocked_from_buffer):
        indexed_text = {
            "content": "indexed text",
            "metadata": {
                "xmpTPg:NPages": 42
            }
        }
        mocked_from_buffer.return_value = indexed_text

        tika = FTLTextExtractionTika()
        doc = Mock()
        tika.process(doc)

        mocked_from_buffer.assert_called_once_with(doc.binary.read())
        self.assertEqual(doc.content_text, indexed_text['content'])
        self.assertEqual(doc.count_pages, indexed_text['metadata']['xmpTPg:NPages'])
        doc.save.assert_called_once()


class ProcPGsqlTests(TestCase):

    def test_process(self):
        pgsql = FTLSearchEnginePgSQLTSVector()
        doc = Mock()
        pgsql.process(doc)

        self.assertEqual(doc.tsvector, SEARCH_VECTOR)
        doc.save.assert_called_once()


class FTLOCRBaseTests(TestCase):

    @patch.object(FTLOCRBase, '_extract_text')
    def test_process(self, mocked_extract_text):
        expected_extracted_text = 'bingo!'
        mocked_extract_text.return_value = expected_extracted_text, 42
        base_ocr = FTLOCRBase()
        base_ocr.supported_storages.append(DEFAULT_FILE_STORAGE)

        # When doc do not have a content text
        mocked_doc = Mock()
        mocked_doc.content_text = ''

        base_ocr.process(mocked_doc)

        # Then OCR _extract_text method is called
        mocked_extract_text.assert_called_once()
        self.assertEqual(mocked_doc.content_text, expected_extracted_text)
        mocked_doc.save.assert_called_once()

        # When doc already have a content text
        mocked_extract_text.reset_mock()
        original_doc_content = ':)'
        mocked_doc = Mock()
        mocked_doc.content_text = original_doc_content

        base_ocr.process(mocked_doc)

        # Then OCR _extract_text method is skipped
        mocked_extract_text.assert_not_called()
        self.assertEqual(mocked_doc.content_text, original_doc_content)
        mocked_doc.save.assert_not_called()

    @patch.object(FTLOCRBase, '_extract_text')
    def test_process_with_invalid_storage(self, mocked_extract_text):
        base_ocr = FTLOCRBase()

        # When DEFAULT_FILE_STORAGE does not match supported storages
        base_ocr.supported_storages.append('this.is.not.the.default.storage')
        mocked_doc = Mock()
        mocked_doc.content_text = ''

        # Then PluginUnsupportedStorage is raised
        with self.assertRaises(PluginUnsupportedStorage):
            base_ocr.process(mocked_doc)
