import logging

import langid

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)

COUNTRY_CODE_INDEX = {
    'fr': 'french',
    'en': 'english',
}


class FTLLangDetectorLangId(FTLDocProcessingBase):
    def __init__(self):
        self.log_prefix = f'[{self.__class__.__name__}]'

    def process(self, ftl_doc, force):
        if force or not ftl_doc.language:
            ftl_doc.language = COUNTRY_CODE_INDEX.get(
                langid.classify(ftl_doc.content_text)[0], 'english'
            )
            ftl_doc.save()
        else:
            logger.debug(f'{self.log_prefix} Skipping Language detect for document {ftl_doc.pid}')
