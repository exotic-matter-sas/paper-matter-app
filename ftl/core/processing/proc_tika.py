#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging

from tika import parser

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)


class FTLTextExtractionTika(FTLDocProcessingBase):
    supported_filetypes = [
        'application/pdf',
        'text/plain',
        'application/rtf',
        'application/msword',
        'application/vnd.ms-excel',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.slide',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]

    def __init__(self):
        self.log_prefix = f'[{self.__class__.__name__}]'

    def process(self, ftl_doc, force):
        parsed_txt = None

        if force or not ftl_doc.count_pages:
            parsed_txt = parser.from_buffer(ftl_doc.binary.read())

            if 'metadata' in parsed_txt and 'xmpTPg:NPages' in parsed_txt['metadata']:
                ftl_doc.count_pages = int(parsed_txt['metadata']['xmpTPg:NPages'])

            else:
                logger.warning(f'{self.log_prefix} Pages number can\'t be retrieved for document {ftl_doc.pid}')
                ftl_doc.count_pages = 1

            ftl_doc.save()
        else:
            logger.debug(f'{self.log_prefix} Skipping Tika extract (page count) for document {ftl_doc.pid}')

        if force or not ftl_doc.content_text:
            if not parsed_txt:
                parsed_txt = parser.from_buffer(ftl_doc.binary.read())

            if 'content' in parsed_txt and parsed_txt["content"]:
                ftl_doc.content_text = parsed_txt["content"].strip()
                ftl_doc.save()
        else:
            logger.debug(f'{self.log_prefix} Skipping Tika extract (text) for document {ftl_doc.pid}')
