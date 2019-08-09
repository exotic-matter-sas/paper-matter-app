import logging

from django.conf import settings
from google.cloud import vision_v1
from google.cloud.vision_v1 import enums

from core.errors import PluginUnsupportedStorage
from core.processing.ftl_processing import FTLOCRBase
from ftl.enums import FTLStorages
from ftl.settings import DEFAULT_FILE_STORAGE

logger = logging.getLogger(__name__)


class FTLOCRGoogleVisionSync(FTLOCRBase):
    """
    Plugin to use Google Vision sync as document OCR.
    It support both Google Cloud Storage and File system storage documents (up to 20 MB, see self.supported_storages).
    Many languages supported: https://cloud.google.com/vision/docs/languages
    API LIMITATION: only the first 5 pages document will be OCRised.
    Doc: https://cloud.google.com/vision/docs/reference/rest/v1/files/annotate
    """

    def __init__(self, credentials=settings.GS_CREDENTIALS):
        super().__init__()
        if DEFAULT_FILE_STORAGE == FTLStorages.GCS:
            self.gcs_bucket_name = settings.GS_BUCKET_NAME
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)
        self.supported_storages = [FTLStorages.FILE_SYSTEM, FTLStorages.GCS]

    def process(self, ftl_doc):
        if DEFAULT_FILE_STORAGE in self.supported_storages:
            # If full text not already extracted
            if not ftl_doc.content_text.strip():
                ftl_doc.content_text = self._extract_text(ftl_doc.binary)
                ftl_doc.save()
            else:
                logger.info(f'{self.log_prefix} Processing skipped, document {ftl_doc.id} already get a text_content')
        else:
            raise PluginUnsupportedStorage(
                f'Plugin {self.__class__.__name__} does not support storage {DEFAULT_FILE_STORAGE} (supported storages '
                f'are: {self.supported_storages}).')

    def _extract_text(self, ftl_doc):
        if DEFAULT_FILE_STORAGE == FTLStorages.GCS:
            storage_uri = f'gs://{self.gcs_bucket_name}/{ftl_doc.name}'
            gcs_source = {'uri': storage_uri}
            input_config = {'gcs_source': gcs_source}
        else:  # Default is FILE_SYSTEM storage
            ftl_doc.open('rb')
            input_config = {'content': ftl_doc.read()}
            ftl_doc.close()

        type_ = enums.Feature.Type.DOCUMENT_TEXT_DETECTION
        features_element = {'type': type_}
        features = [features_element]

        # The service can process up to 5 pages per document file.
        # Here we specify the first, second, and last page of the document to be
        # processed.
        requests_element = {'input_config': input_config, 'features': features}
        requests = [requests_element]

        response = self.client.batch_annotate_files(requests)

        return "\n".join([e.full_text_annotation.text for e in response.responses[0].responses])