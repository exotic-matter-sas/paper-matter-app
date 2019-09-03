import logging

from tika import parser

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)


class FTLTextExtractionTika(FTLDocProcessingBase):
    def __init__(self):
        self.log_prefix = f'[{self.__class__.__name__}]'

    def process(self, ftl_doc, force):
        parsed_txt = None

        if force or not ftl_doc.count_pages:
            parsed_txt = parser.from_buffer(ftl_doc.binary.read())

            if 'metadata' in parsed_txt and 'xmpTPg:NPages' in parsed_txt['metadata']:
                ftl_doc.count_pages = parsed_txt['metadata']['xmpTPg:NPages']
                ftl_doc.save()
            else:
                logger.warning(f'{self.log_prefix} Pages number can\'t be retrieved for document {ftl_doc.pid}')
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
