from tika import parser

from core.processing.ftl_processing import FTLDocProcessingBase


class FTLTextExtractionTika(FTLDocProcessingBase):
    def process(self, ftl_doc):
        parsed_txt = parser.from_buffer(ftl_doc.binary.read())
        if 'content' in parsed_txt and parsed_txt["content"]:
            ftl_doc.content_text = parsed_txt["content"].strip()
            ftl_doc.save()
