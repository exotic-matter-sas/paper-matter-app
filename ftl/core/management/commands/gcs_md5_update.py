#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import base64

from django.core.management import BaseCommand
from storages.backends.gcloud import GoogleCloudFile

from core.models import FTLDocument


class Command(BaseCommand):
    help = "Update documents with MD5 from GCS"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Starting update of MD5 hash from Google Storage"
            )
        )
        documents = FTLDocument.objects.filter(md5__isnull=True, deleted=False)

        for doc in documents:
            try:
                if doc.binary.file and isinstance(doc.binary.file, GoogleCloudFile):
                    doc.md5 = base64.urlsafe_b64decode(
                        doc.binary.file.blob.md5_hash
                    ).hex()
                    doc.save()
                    self.stdout.write(f"Updated {doc.pid} with {doc.md5}")
            except IOError:
                pass
