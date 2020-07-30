#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils.module_loading import import_string

from core.errors import PluginUnsupportedStorage
from core.models import FTLDocument
from core.signals import pre_ftl_processing
from ftl.settings import DEFAULT_FILE_STORAGE

logger = logging.getLogger(__name__)


class FTLDocProcessingBase:
    supported_documents_types = []  # mimetype of supported file format or * for all

    def process(self, ftl_doc, force):
        raise NotImplementedError


class FTLDocumentProcessing:
    """
    A generic document processing class, to be used for adding processing to document such as OCR,
    text extraction, etc.
    """

    def __init__(self, configured_plugins=settings.FTL_DOC_PROCESSING_PLUGINS):
        self.plugins = list()

        for configured_plugin in configured_plugins:
            my_class = import_string(configured_plugin)

            if (
                issubclass(my_class, FTLDocProcessingBase)
                and my_class is not FTLDocProcessingBase
            ):
                self.plugins.append(my_class())

    def apply_processing(self, ftl_doc, force=False):
        self._handle(ftl_doc, force=force)
        logger.info(f"{ftl_doc.pid} submitted to docs processing")

    def _handle(self, ftl_doc, force):
        plugins_all = True if isinstance(force, bool) and force else False
        plugins_forced = force if isinstance(force, list) else []
        errors = list()
        # for each registered processing plugin, apply processing
        for plugin in self.plugins:
            if (
                ftl_doc.type in plugin.supported_documents_types
                or "*" in plugin.supported_documents_types
            ):
                try:
                    logger.debug(
                        f"Executing plugin {plugin.__class__.__name__} on {ftl_doc.pid}"
                    )
                    pre_ftl_processing.send(sender=plugin.__class__, document=ftl_doc)

                    # Refresh model to have latest update if any
                    ftl_doc.refresh_from_db()
                    plugin.process(
                        ftl_doc,
                        plugins_all
                        or ".".join(
                            [plugin.__class__.__module__, plugin.__class__.__qualname__]
                        )
                        in plugins_forced,
                    )
                except Exception:
                    errors.append(plugin.__class__.__name__)
                    logger.exception(
                        f"Error while processing {ftl_doc.pid} with plugin {plugin.__class__.__name__}"
                    )
            else:
                logger.debug(
                    f"Skipping plugin {plugin.__class__.__name__} on {ftl_doc.pid} (mimetype not supported)"
                )

        if errors:
            logger.error(
                f"{ftl_doc.pid} was processed by {len(self.plugins)} plugins ({len(errors)} failing: "
                f'{", ".join(errors)})'
            )
        else:
            logger.info(f"{ftl_doc.pid} was processed correctly")


class FTLOCRBase(FTLDocProcessingBase):
    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"
        self.supported_storages = []

    def process(self, ftl_doc, force):
        if DEFAULT_FILE_STORAGE in self.supported_storages:
            # If full text not already extracted
            if force or not ftl_doc.content_text.strip():
                extracted_text = self._extract_text(ftl_doc.binary)

                atomic_ftl_doc_update(
                    ftl_doc.pid, {"content_text": extracted_text, "ocrized": True}
                )
            else:
                logger.info(
                    f"{self.log_prefix} Processing skipped, document {ftl_doc.id} already got a text_content"
                )
        else:
            raise PluginUnsupportedStorage(
                f"{self.log_prefix} does not support storage {DEFAULT_FILE_STORAGE} (supported storage are: "
                f"{self.supported_storages})."
            )

    def _extract_text(self, ftl_doc_binary):
        raise NotImplementedError


def atomic_ftl_doc_update(pid: UUID, values: dict):
    """
        Atomically update FTLDocument with the specified fields `values`
        Example usage:  atomic_ftl_doc_update(pid, {"content": "my value"})
    """
    # Issue #161
    with transaction.atomic():
        ftl_doc_update = FTLDocument.objects.select_for_update().get(pid=pid)
        keys = list()
        for key, value in values.items():
            keys.append(key)
            setattr(ftl_doc_update, key, value)

        ftl_doc_update.save(update_fields=keys)
