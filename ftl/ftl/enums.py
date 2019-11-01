class FTLStorages:
    """
    Enum of supported storages

    FILE_SYSTEM, default storage, store documents locally on file system
    AWS_S3, store documents remotely on Amazon S3 bucket
    - Extra python modules required: django-storages, boto3 (see requirements.txt)
    GCS, store documents remotely on Google Cloud Storage
    - Extra python modules required: django-storages + google-cloud-storage (see requirements.txt)
    """
    FILE_SYSTEM = 'django.core.files.storage.FileSystemStorage'
    AWS_S3 = 'storages.backends.s3boto3.S3Boto3Storage'
    GCS = 'storages.backends.gcloud.GoogleCloudStorage'


class FTLPlugins:
    """
    Enum of supported plugins

    Plugins extra requirements :
    OCR_AWS_TEXTRACT
    - Require to store documents on Amazon S3 (see DEFAULT_FILE_STORAGE in settings)
    OCR_GOOGLE_VISION_SYNC
    - Require to store documents on File system storage or Google cloud storage (see DEFAULT_FILE_STORAGE in settings)
    - Extra python module required: google-cloud-vision (see requirements.txt)
    OCR_GOOGLE_VISION_ASYNC
    - Require to store documents on Google cloud storage (see DEFAULT_FILE_STORAGE in settings)
    - Extra python module required: google-cloud-vision (see requirements.txt)
    """
    TEXT_EXTRACTION_TIKA = 'core.processing.proc_tika.FTLTextExtractionTika'

    OCR_AWS_TEXTRACT = 'core.processing.proc_aws_textract.FTLOCRAwsTextract'
    OCR_GOOGLE_VISION_SYNC = 'core.processing.proc_google_vision_sync.FTLOCRGoogleVisionSync'
    OCR_GOOGLE_VISION_ASYNC = 'core.processing.proc_google_vision_async.FTLOCRGoogleVisionAsync'

    LANG_DETECTOR_LANGID = 'core.processing.proc_lang.FTLLangDetectorLangId'
    SEARCH_ENGINE_PGSQL_TSVECTOR = 'core.processing.proc_pgsql_tsvector.FTLSearchEnginePgSQLTSVector'

    @staticmethod
    def get_value(name):
        try:
            value = getattr(FTLPlugins, name.upper())
            if not callable(value):
                return value
            else:
                return None
        except AttributeError:
            return None
