#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import logging

from tika import parser

from core.processing.ftl_processing import FTLDocProcessingBase, atomic_ftl_doc_update

logger = logging.getLogger(__name__)


class FTLTextExtractionTika(FTLDocProcessingBase):
    supported_documents_types = [
        "application/pdf",
        "text/plain",
        "application/rtf",
        "application/msword",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.slide",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.presentation",
        "application/vnd.oasis.opendocument.spreadsheet",
    ]

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"

    def process(self, ftl_doc, force):
        parsed_txt = None

        if force or not ftl_doc.count_pages:
            with ftl_doc.binary.open("rb") as ff:
                parsed_txt = parser.from_buffer(ff.read())

            if "metadata" in parsed_txt and "xmpTPg:NPages" in parsed_txt["metadata"]:
                atomic_ftl_doc_update(
                    ftl_doc.pid,
                    {"count_pages": int(parsed_txt["metadata"]["xmpTPg:NPages"])},
                )
            else:
                logger.warning(
                    f"{self.log_prefix} Pages number can't be retrieved for document {ftl_doc.pid}"
                )

        else:
            logger.debug(
                f"{self.log_prefix} Skipping Tika extract (page count) for document {ftl_doc.pid}"
            )

        if force or not ftl_doc.content_text:
            if not parsed_txt:
                with ftl_doc.binary.open("rb") as ff:
                    parsed_txt = parser.from_buffer(ff.read())

            if "content" in parsed_txt and parsed_txt["content"]:
                atomic_ftl_doc_update(
                    ftl_doc.pid, {"content_text": parsed_txt["content"].strip()}
                )
        else:
            logger.debug(
                f"{self.log_prefix} Skipping Tika extract (text) for document {ftl_doc.pid}"
            )
