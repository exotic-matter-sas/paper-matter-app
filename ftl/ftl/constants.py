class FTLStorages:
    FILE_SYSTEM = 'django.core.files.storage.FileSystemStorage'
    AWS_S3 = 'storages.backends.s3boto3.S3Boto3Storage'
    GCS = 'storages.backends.gcloud.GoogleCloudStorage'
