import logging
import re

from django.conf import settings
from google.cloud import storage
from google.cloud import vision
from google.cloud import vision_v1
from google.protobuf import json_format

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)


class FTLOCRGoogleVisionAsync(FTLDocProcessingBase):
    """
    Plugin to use Google Vision as document OCR.
    Currently plugin support Google Cloud Storage hosted documents only
    """

    def __init__(self, credentials=settings.GS_CREDENTIALS, gcs_bucket_name=settings.GS_BUCKET_NAME):
        self.log_prefix = f'[{self.__class__.__name__}]'
        self.gcs_bucket_name = gcs_bucket_name
        self.bucket = storage.Client(project=credentials.project_id, credentials=credentials).get_bucket(
            gcs_bucket_name)
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)

        self.mime_type = 'application/pdf'
        self.batch_size = 10  # How many pages should be grouped into each json output file
        self.feature = vision.types.Feature(type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

    def process(self, ftl_doc):
        # TODO raise a specific error if file storage not supported
        # If full text not already extracted
        if not ftl_doc.content_text.strip():
            ftl_doc.content_text = self._async_detect_document(ftl_doc.binary)
            ftl_doc.save()
        else:
            logger.info(f'{self.log_prefix} Processing skipped, document {ftl_doc.id} already get a text_content')

    def _async_detect_document(self, ftl_doc_binary):
        storage_uri = f'gs://{self.gcs_bucket_name}/{ftl_doc_binary.name}'
        storage_uri_ocr_target = f'gs://{self.gcs_bucket_name}/{ftl_doc_binary.name}.ocr.json'

        gcs_source = vision.types.GcsSource(uri=storage_uri)
        input_config = vision.types.InputConfig(
            gcs_source=gcs_source, mime_type=self.mime_type)

        gcs_destination = vision.types.GcsDestination(uri=storage_uri_ocr_target)
        output_config = vision.types.OutputConfig(
            gcs_destination=gcs_destination, batch_size=self.batch_size)

        async_request = vision.types.AsyncAnnotateFileRequest(
            features=[self.feature], input_config=input_config,
            output_config=output_config)

        operation = self.client.async_batch_annotate_files(
            requests=[async_request])

        # Wait for the OCR to finish
        operation.result(timeout=None)

        # Once the request has completed and the output has been
        # written to GCS, we can list all the output files.
        match = re.match(r'gs://([^/]+)/(.+)', storage_uri_ocr_target)
        prefix = match.group(2)

        # List objects with the given prefix.
        blob_list = list(self.bucket.list_blobs(prefix=prefix))
        pages_text = list()

        for blob in blob_list:
            json_string = blob.download_as_string()
            response = json_format.Parse(
                json_string, vision.types.AnnotateFileResponse())

            for response in response.responses:
                pages_text.append(response.full_text_annotation.text)

        return "\n".join(pages_text)
