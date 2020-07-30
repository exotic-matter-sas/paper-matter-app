#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging

from django.contrib.postgres.search import SearchVector
from django.db.models import F

from core.processing.ftl_processing import FTLDocProcessingBase, atomic_ftl_doc_update

logger = logging.getLogger(__name__)

SEARCH_VECTOR = (
    SearchVector("content_text", weight="C", config=F("language"))
    + SearchVector("note", weight="B", config=F("language"))
    + SearchVector("title", weight="A", config=F("language"))
)


class FTLSearchEnginePgSQLTSVector(FTLDocProcessingBase):
    supported_documents_types = ["*"]

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"

    def process(self, ftl_doc, force):
        if force or not ftl_doc.tsvector:
            atomic_ftl_doc_update(ftl_doc.pid, {"tsvector": SEARCH_VECTOR})
        else:
            logger.debug(
                f"{self.log_prefix} Skipping tsvector compute for document {ftl_doc.pid}"
            )
