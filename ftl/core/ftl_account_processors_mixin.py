#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
from django.conf import settings
from django.utils.module_loading import import_string
from django.views.generic.base import ContextMixin

from ftl.utils import initialize_static


@initialize_static
class FTLAccountProcessorContextMixin(ContextMixin):
    """
    This is a custom processor for ftl apps, allow injecting account data in the frontend Vue app
    Also allow injecting data from others apps
    See FTL_ACCOUNT_PROCESSORS in settings.py
    """

    plugins = []

    @classmethod
    def init_static(cls):
        # Only load plugins at first class instanciation
        if not cls.plugins:
            plugins_to_load = getattr(settings, "FTL_ACCOUNT_PROCESSORS", [])

            cls.plugins = list()
            for configured_plugin in plugins_to_load:
                my_class = import_string(configured_plugin)
                cls.plugins.append(my_class)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        _request = getattr(self, "request", None)

        ftl_context = {}
        if _request:
            for plugin in FTLAccountProcessorContextMixin.plugins:
                ftl_context.update(plugin(_request))

        context_data["ftl_account"] = ftl_context

        return context_data
