from django.conf import settings
from google.cloud import vision_v1
from google.cloud.vision_v1 import enums

from core.processing.ftl_processing import FTLDocProcessingBase


class FTLOCRGoogleVision(FTLDocProcessingBase):
    client = vision_v1.ImageAnnotatorClient()

    def __init__(self, gcs_bucket_name=settings.GS_BUCKET_NAME):
        self.gcs_bucket_name = gcs_bucket_name

    def process(self, ftl_doc):
        ftl_doc.content_text = self._sample_batch_annotate_files(ftl_doc.binary)
        ftl_doc.save()

    def _sample_batch_annotate_files(self, ftl_doc):
        storage_uri = f'gs://{self.gcs_bucket_name}/{ftl_doc.name}'
        # storage_uri = 'gs://cloud-samples-data/vision/document_understanding/kafka.pdf'

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
        # for image_response in response.responses[0].responses:
        #     print('Full text: {}'.format(image_response.full_text_annotation.text))

        return " ".join([e.full_text_annotation.text for e in response.responses[0].responses])
