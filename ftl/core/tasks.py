#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from celery import shared_task
from django.conf import settings

from core.models import FTLDocument
from core.processing.ftl_processing_celery import FTLDocumentProcessingCelery


@shared_task
def apply_ftl_processing(ftl_doc_pk, force: bool):
    doc = FTLDocument.objects.get(pk=ftl_doc_pk)
    ftl_document_processing_celery = FTLDocumentProcessingCelery(
        settings.FTL_DOC_PROCESSING_PLUGINS
    )
    ftl_document_processing_celery.apply_processing(doc, force)
