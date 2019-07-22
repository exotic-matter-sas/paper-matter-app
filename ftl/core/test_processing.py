from unittest import TestCase
from unittest.mock import Mock

from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase


class FTLDocumentProcessingTests(TestCase):
    def setUp(self):
        configured_plugins = ['core.test_processing']
        self.processing = FTLDocumentProcessing(configured_plugins)

    def test_plugins_loading(self):
        self.assertIsNotNone(self.processing.plugins)
        self.assertTrue(isinstance(self.processing.plugins[0], ProcTest))

    def test_apply_processing(self):
        self.processing.executor.submit = Mock()

        doc = Mock()
        self.processing.apply_processing(doc)

        self.processing.executor.submit.assert_called_once_with(self.processing._handle, doc)

    def test_handle(self):
        mock_plugin = Mock(spec=ProcTest)
        self.processing.plugins[0] = mock_plugin

        doc = Mock()
        self.processing.apply_processing(doc)

        mock_plugin.process.assert_called_once_with(doc)


class ProcTest(FTLDocProcessingBase):

    def process(self, ftl_doc):
        pass
