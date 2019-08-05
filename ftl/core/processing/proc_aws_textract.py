import logging
import time

import boto3
from django.conf import settings

from core.errors import PluginUnsupportedStorage
from core.processing.ftl_processing import FTLDocProcessingBase
from ftl.enums import FTLStorages
from ftl.settings import DEFAULT_FILE_STORAGE

logger = logging.getLogger(__name__)


class FTLOCRAwsTextract(FTLDocProcessingBase):
    """
    Plugin to use Amazon Textract service as document OCR.
    Support Amazon S3 bucket hosted documents only (see self.supported_storages).
    Doc: https://docs.aws.amazon.com/fr_fr/textract/latest/dg/API_StartDocumentAnalysis.html
    """
    def __init__(self, aws_bucket=settings.AWS_STORAGE_BUCKET_NAME):
        self.log_prefix = f'[{self.__class__.__name__}]'
        self.aws_bucket = aws_bucket
        self.client = boto3.client(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            service_name='textract',
            region_name='eu-west-1',
            endpoint_url='https://textract.eu-west-1.amazonaws.com',
        )
        self.supported_storages = [FTLStorages.AWS_S3]

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

    def _extract_text(self, ftl_doc_binary):
        document_name = ftl_doc_binary.name

        job_id = self._start_job(self.aws_bucket, document_name)

        first_response_chunk = self._get_job_response_once_completed(job_id)
        if first_response_chunk['JobStatus'] in ['SUCCEEDED', 'PARTIAL_SUCCESS']:
            if first_response_chunk['JobStatus'] == 'PARTIAL_SUCCESS':
                logger.warning(f'{self.log_prefix} Text extraction only partial (Amazon side)')
            response_chunks = self._get_all_response_chunks(job_id, first_response_chunk)

            text_lines = list()
            for chunk in response_chunks:
                for item in chunk["Blocks"]:
                    if item["BlockType"] == "LINE":
                        text_lines.append(item["Text"])

            return "\n".join(text_lines)
        else:  # JobStatus is FAILED
            logger.error(f'{self.log_prefix} Text extraction failed (Amazon side)')
            return ""

    def _start_job(self, s3_bucket_name, object_name):
        response = self.client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3_bucket_name,
                    'Name': object_name
                }
            })

        return response["JobId"]

    def _get_job_response_once_completed(self, job_id):
        first_iteration = True
        status = None
        response = {}

        while first_iteration or status == "IN_PROGRESS":
            time.sleep(5)
            response = self.client.get_document_text_detection(JobId=job_id)
            status = response["JobStatus"]
            first_iteration = False

        return response

    def _get_all_response_chunks(self, job_id, first_response_chunk):
        response_chunks = [first_response_chunk]
        next_token = first_response_chunk['NextToken'] if 'NextToken' in first_response_chunk else None

        while next_token:
            time.sleep(5)

            response = self.client.get_document_text_detection(JobId=job_id, NextToken=next_token)

            response_chunks.append(response)
            next_token = response['NextToken'] if 'NextToken' in response else None

        return response_chunks
