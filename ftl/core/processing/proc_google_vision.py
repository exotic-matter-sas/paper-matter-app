import logging

from django.conf import settings
from google.cloud import vision_v1
from google.cloud.vision_v1 import enums

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)


class FTLOCRGoogleVision(FTLDocProcessingBase):
    """
    Plugin to use Google Vision as document OCR.
    API LIMITATION: only the first 5 pages of document will be OCRised
    It support both Google Cloud Storage and File system storage documents
    """
    client = vision_v1.ImageAnnotatorClient()

    def __init__(self, gcs_bucket_name=settings.GS_BUCKET_NAME):
        self.log_prefix = f'[{self.__class__.__name__}]'
        self.gcs_bucket_name = gcs_bucket_name

    def process(self, ftl_doc):
        # TODO raise a specific error if file storage not supported
        # If full text not already extracted
        if not ftl_doc.content.text.strip():
            ftl_doc.content_text = self._sample_batch_annotate_files(ftl_doc.binary)
            ftl_doc.save()
        else:
            logger.info(f'{self.log_prefix} Processing skipped, document {ftl_doc.id} already get a text_content')

    def _sample_batch_annotate_files(self, ftl_doc):
        # TODO add support for FILE_SYSTEM storage
        storage_uri = f'gs://{self.gcs_bucket_name}/{ftl_doc.name}'

        gcs_source = {'uri': storage_uri}
        input_config = {'gcs_source': gcs_source}
        type_ = enums.Feature.Type.DOCUMENT_TEXT_DETECTION
        features_element = {'type': type_}
        features = [features_element]

        # The service can process up to 5 pages per document file.
        # Here we specify the first, second, and last page of the document to be
        # processed.
        pages_element = 1
        pages_element_2 = -1
        pages = [pages_element, pages_element_2]
        requests_element = {'input_config': input_config, 'features': features, 'pages': pages}
        requests = [requests_element]

        response = self.client.batch_annotate_files(requests)

        return "\n".join([e.full_text_annotation.text for e in response.responses[0].responses])
