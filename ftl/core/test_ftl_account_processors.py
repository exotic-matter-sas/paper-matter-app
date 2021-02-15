#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

from django.test import RequestFactory, SimpleTestCase

from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin


def mock_processor(request):
    return {"test": True}


def mock_processor_bis(request):
    return {"test_2": 1234}


class FTLAccountProcessorContextMixinTests(SimpleTestCase):
    def setUp(self):
        self.processor = FTLAccountProcessorContextMixin()
        # Force rewrite of the plugin list (override_settings doesn't work here)
        FTLAccountProcessorContextMixin.plugins = [mock_processor, mock_processor_bis]

    def test_plugins_loading(self):
        self.assertTrue(len(self.processor.plugins) == 2)
        instance = self.processor.plugins[0]
        instance_bis = self.processor.plugins[1]
        self.assertTrue(instance == mock_processor)
        self.assertTrue(instance_bis == mock_processor_bis)

    def test_get_context_data(self):
        rf = RequestFactory()
        self.processor.request = rf.get("/hello/")
        context_data = self.processor.get_context_data()

        self.assertIn("ftl_account", context_data)
        self.assertDictEqual(
            context_data["ftl_account"], {"test": True, "test_2": 1234}
        )
