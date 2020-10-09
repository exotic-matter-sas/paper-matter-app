#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.test import RequestFactory, SimpleTestCase, override_settings

from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin


def mock_processor(request):
    return {"test": True}


@override_settings(
    FTL_ACCOUNT_PROCESSORS=["core.test_ftl_account_processors.mock_processor"]
)
class FTLAccountProcessorContextMixinTests(SimpleTestCase):
    def setUp(self):
        self.processor = FTLAccountProcessorContextMixin()

    def test_plugins_loading(self):
        instance = self.processor.plugins[0]
        self.assertTrue(instance == mock_processor)

    def test_get_context_data_with_request(self):
        rf = RequestFactory()
        get_request = rf.get("/hello/")
        context_data = self.processor.get_context_data_with_request(get_request)

        self.assertIn("ftl_account", context_data)
        self.assertEqual(context_data["ftl_account"], {"test": True})
