from unittest import TestCase
from unittest.mock import Mock, patch

import langid
from tika import parser

from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase
from core.processing.proc_lang import FTLDocLangDetector
from core.processing.proc_pgsql_tsvector import FTLDocPgSQLTSVector, SEARCH_VECTOR
from core.processing.proc_tika import FTLDocTextExtractionTika


class FTLDocumentProcessingTests(TestCase):
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
        mock_plugin = Mock(spec=ProcTest)
        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin)

        doc = Mock()
        self.processing.apply_processing(doc)

        mock_plugin.process.assert_called_once_with(doc)


class FTLProcLangTests(TestCase):

    @patch.object(langid, 'classify')
    def test_process(self, mock_langid):
        mock_langid.return_value = ['fr']

        lang = FTLDocLangDetector()
        doc = Mock()
        lang.process(doc)

        mock_langid.assert_called_once_with(doc.content_text)
        self.assertEqual('french', doc.language)
        doc.save.assert_called_once()


class FTLProcTikaTests(TestCase):

    @patch.object(parser, 'from_buffer')
    def test_process(self, mock_parser):
        indexed_text_ = {"content": "indexed text"}
        mock_parser.return_value = indexed_text_

        tika = FTLDocTextExtractionTika()
        doc = Mock()
        tika.process(doc)

        mock_parser.assert_called_once_with(doc.binary.read())
        self.assertEqual(doc.content_text, indexed_text_['content'])
        doc.save.assert_called_once()


class FTLProcPGsqlTests(TestCase):

    def test_process(self):
        pgsql = FTLDocPgSQLTSVector()
        doc = Mock()
        pgsql.process(doc)

        self.assertEqual(doc.tsvector, SEARCH_VECTOR)
        doc.save.assert_called_once()


class ProcTest(FTLDocProcessingBase):
    """
    Test processing class
    """

    def process(self, ftl_doc):
        pass
