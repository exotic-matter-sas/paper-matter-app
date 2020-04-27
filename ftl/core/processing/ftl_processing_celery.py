#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging
from pydoc import locate

from core.processing.ftl_processing import FTLDocumentProcessing, FTLDocProcessingBase

logger = logging.getLogger(__name__)


class FTLDocumentProcessingCelery(FTLDocumentProcessing):
    def __init__(self, configured_plugins):
        self.plugins = list()

        for configured_plugin in configured_plugins:
            my_class = locate(configured_plugin)

            if (
                issubclass(my_class, FTLDocProcessingBase)
                and my_class is not FTLDocProcessingBase
            ):
                self.plugins.append(my_class())

    def apply_processing(self, ftl_doc, force=False):
        logger.info(f"{ftl_doc.pid} submitted to docs processing")
        self._handle(ftl_doc, force=force)
