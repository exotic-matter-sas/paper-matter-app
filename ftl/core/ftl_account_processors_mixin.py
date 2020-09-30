#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.conf import settings
from django.utils.module_loading import import_string
from django.views.generic.base import ContextMixin


class FTLAccountProcessorMixin(ContextMixin):
    plugins = list()

    # This is a custom processor for ftl apps, allow injecting account data in the frontend Vue app
    # Also allow injecting data from others apps
    # See FTL_ACCOUNT_PROCESSORS in settings.py
    for configured_plugin in getattr(settings, "FTL_ACCOUNT_PROCESSORS", []):
        my_class = import_string(configured_plugin)
        plugins.append(my_class)

    def get_context_data_with_request(self, request, **kwargs):
        context_data = super().get_context_data(**kwargs)

        ftl_context = {}
        for plugin in self.__class__.plugins:
            ftl_context = {**ftl_context, **plugin(request)}

        context_data["ftl_account"] = ftl_context

        return context_data
