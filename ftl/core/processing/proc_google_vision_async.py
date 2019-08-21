import logging

from django.conf import settings
from google.cloud import storage
from google.cloud import vision
from google.cloud import vision_v1
from google.protobuf import json_format

from core.processing.ftl_processing import FTLOCRBase
from ftl.enums import FTLStorages

logger = logging.getLogger(__name__)


class FTLOCRGoogleVisionAsync(FTLOCRBase):
    """
    Plugin to use Google Vision async as document OCR.
    Support Google Cloud Storage hosted documents only (self.supported_storages).
    Many languages supported: https://cloud.google.com/vision/docs/languages
    Doc: https://cloud.google.com/vision/docs/reference/rest/v1/files/asyncBatchAnnotate
    """

    def __init__(self, credentials=settings.GS_CREDENTIALS, gcs_bucket_name=settings.GS_BUCKET_NAME):
        super().__init__()
        self.gcs_bucket_name = gcs_bucket_name
        self.bucket = storage.Client(project=credentials.project_id, credentials=credentials).get_bucket(
            gcs_bucket_name)
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)
        self.supported_storages = [FTLStorages.GCS]

        self.mime_type = 'application/pdf'
        self.batch_size = 10  # How many pages should be grouped into each json output file
        self.feature = vision.types.Feature(type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

    def _extract_text(self, ftl_doc_binary):
        storage_uri = f'gs://{self.gcs_bucket_name}/{ftl_doc_binary.name}'
        # This will used by Google to generate a filename like this:
        # 1ac7b8e9-ecc6-4522-9948-1775f188feaa.pdf.ocr.output-1-to-1.json
        storage_uri_ocr_target = f'gs://{self.gcs_bucket_name}/{ftl_doc_binary.name}.ocr.'

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
        # Example output file: 1ac7b8e9-ecc6-4522-9948-1775f188feaa.pdf.ocr.output-1-to-1.json
        prefix = f'{ftl_doc_binary.name}.ocr.'

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
