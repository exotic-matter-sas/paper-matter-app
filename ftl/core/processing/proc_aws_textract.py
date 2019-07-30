import time

import boto3
from django.conf import settings

from core.processing.ftl_processing import FTLDocProcessingBase


class FTLAwsTextract(FTLDocProcessingBase):
    """
    Plugin to use Amazon Textract service as document OCR.
    Document have to stored on a Amazon S3 bucket for this plugin to work.
    """
    def __init__(self, aws_bucket=settings.AWS_STORAGE_BUCKET_NAME):
        self.aws_bucket = aws_bucket
        self.client = boto3.client(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            service_name='textract',
            region_name='eu-west-1',
            endpoint_url='https://textract.eu-west-1.amazonaws.com',
        )

    def process(self, ftl_doc):
        ftl_doc.content_text = self._batch(ftl_doc.binary)
        ftl_doc.save()

    def _batch(self, ftl_doc_binary):
        document_name = ftl_doc_binary.name

        job_id = self._start_job(self.aws_bucket, document_name)
        if self._is_job_complete(job_id):
            response = self._get_job_results(job_id)

            text_lines = list()
            for resultPage in response:
                for item in resultPage["Blocks"]:
                    if item["BlockType"] == "LINE":
                        text_lines.append(item["Text"])

            return " ".join(text_lines)
        else:
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

    def _is_job_complete(self, job_id):
        time.sleep(5)
        response = self.client.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]
        # print("Job status: {}".format(status))

        while status == "IN_PROGRESS":
            time.sleep(5)
            response = self.client.get_document_text_detection(JobId=job_id)
            status = response["JobStatus"]
            # print("Job status: {}".format(status))

        return status

    def _get_job_results(self, job_id):
        pages = []

        time.sleep(5)

        response = self.client.get_document_text_detection(JobId=job_id)

        pages.append(response)
        next_token = None
        if 'NextToken' in response:
            next_token = response['NextToken']

        while next_token:
            time.sleep(5)

            response = self.client.get_document_text_detection(JobId=job_id, NextToken=next_token)

            pages.append(response)
            next_token = None
            if 'NextToken' in response:
                next_token = response['NextToken']

        return pages
