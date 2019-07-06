import time

from django.core.management import BaseCommand

from core.models import FTLDocument
from core.processing.ftl_processing import FTLDocumentProcessing


class Command(BaseCommand):
    help = 'Reindex all documents'

    def handle(self, *args, **options):
        processing = FTLDocumentProcessing()
        docs = FTLDocument.objects.all()

        start_time = time.time()
        documents_count = len(docs)
        s = "s" if documents_count > 1 else ""
        self.stdout.write(self.style.MIGRATE_HEADING(f'Starting to reindex {documents_count} document{s}'))

        for doc in docs:
            processing.apply_processing(doc)
            self.stdout.write(self.style.SUCCESS(f'Submitted {doc.title} for processing'))

        # Wait for all processing
        processing.executor.shutdown(True)

        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(f'{documents_count} document{s} successfully reindexed in'
                                             f' {round(end_time - start_time, 2)}s'))
