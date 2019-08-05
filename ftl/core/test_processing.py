from unittest import TestCase, skip
from unittest.mock import Mock, patch

import langid
from tika import parser

from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase
from core.processing.proc_lang import FTLLangDetectorLangId
from core.processing.proc_pgsql_tsvector import FTLSearchEnginePgSQLTSVector, SEARCH_VECTOR
from core.processing.proc_tika import FTLTextExtractionTika


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
        mock_plugin_1 = Mock(spec=ProcTest)
        mock_plugin_2 = Mock(spec=ProcTest)
        mock_plugin_3 = Mock(spec=ProcTest)

        self.processing.plugins = list()
        self.processing.plugins.append(mock_plugin_1)
        self.processing.plugins.append(mock_plugin_2)
        self.processing.plugins.append(mock_plugin_3)

        doc = Mock()
        self.processing.apply_processing(doc)

        mock_plugin_1.process.assert_called_once_with(doc)
        mock_plugin_2.process.assert_called_once_with(doc)
        mock_plugin_3.process.assert_called_once_with(doc)

    @skip('TODO')  # TODO
    def test_error_handling(self):
        pass


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
        indexed_text = {"content": "indexed text"}
        mocked_from_buffer.return_value = indexed_text

        tika = FTLTextExtractionTika()
        doc = Mock()
        tika.process(doc)

        mocked_from_buffer.assert_called_once_with(doc.binary.read())
        self.assertEqual(doc.content_text, indexed_text['content'])
        doc.save.assert_called_once()


class ProcPGsqlTests(TestCase):

    def test_process(self):
        pgsql = FTLSearchEnginePgSQLTSVector()
        doc = Mock()
        pgsql.process(doc)

        self.assertEqual(doc.tsvector, SEARCH_VECTOR)
        doc.save.assert_called_once()


class ProcAwsTextractTests(TestCase):

    @skip('TODO')  # TODO
    def test_process(self):
        pass


class ProcGoogleVisionTests(TestCase):

    @skip('TODO')  # TODO
    def test_process(self):
        pass


class ProcOcrMyPdfTests(TestCase):

    @skip('TODO')  # TODO
    def test_process(self):
        pass
