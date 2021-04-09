#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import datetime
from unittest.mock import patch

from django.contrib.sessions.backends.base import SessionBase
from django.test import RequestFactory, SimpleTestCase, TestCase

from core import ftl_account_processor
from core.ftl_account_processor import ftl_account_data
from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin
from ftests.tools.setup_helpers import setup_org, setup_user


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


class FTLAccountDataTests(TestCase):
    def setUp(self):
        self.org = setup_org()
        self.user = setup_user(self.org)

    @patch.object(ftl_account_processor, "datetime")
    def test_non_existant_time(self, mock_dt):
        # This is the DST transition period in France (2am->3am)
        mock_dt.datetime.utcnow.return_value = datetime.datetime(2021, 3, 28, 2, 31, 7)
        rf = RequestFactory()
        rf.user = self.user
        rf.session = SessionBase()

        ftl_account_data(rf)
