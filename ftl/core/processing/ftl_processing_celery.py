#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging
from pydoc import locate

from django.conf import settings

from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase

logger = logging.getLogger(__name__)

PLUGINS_PROC = set()
for configured_plugin in settings.FTL_DOC_PROCESSING_PLUGINS:
    my_class = locate(configured_plugin)

    if (
        issubclass(my_class, FTLDocProcessingBase)
        and my_class is not FTLDocProcessingBase
    ):
        PLUGINS_PROC.add(my_class())


class FTLDocumentProcessingCelery(FTLDocumentProcessing):
    def __init__(self, configured_plugins=None, max_workers=None):
        self.plugins = list(PLUGINS_PROC)

    def apply_processing(self, ftl_doc, force=False):
        logger.info(f"{ftl_doc.pid} submitted to docs processing")
        self._handle(ftl_doc, force=force)
