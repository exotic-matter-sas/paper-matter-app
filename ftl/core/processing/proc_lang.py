import langid

from core.processing.ftl_processing import FTLDocProcessingBase

COUNTRY_CODE_INDEX = {
    'fr': 'french',
    'en': 'english',
}


class FTLLangDetectorLangId(FTLDocProcessingBase):
    def process(self, ftl_doc):
        ftl_doc.language = COUNTRY_CODE_INDEX.get(
            langid.classify(ftl_doc.content_text)[0], 'english'
        )
        ftl_doc.save()
