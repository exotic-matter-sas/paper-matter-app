import time

from django.core.management import BaseCommand

from core.models import FTLDocument
from core.views import _extract_text_from_pdf, SEARCH_VECTOR


class Command(BaseCommand):
    help = 'Reindex all documents'

    def handle(self, *args, **options):
        docs = FTLDocument.objects.all()

        start_time = time.time()
        documents_count = len(docs)
        s = "s" if documents_count > 1 else ""
        self.stdout.write(self.style.MIGRATE_HEADING(f'Starting to reindex {documents_count} document{s}'))

        for doc in docs:
            _extract_text_from_pdf(SEARCH_VECTOR, doc)

            self.stdout.write(self.style.SUCCESS(f'Reindexed {doc.title}'))
        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(f'{documents_count} document{s} successfully reindexed in'
                                             f' {round(end_time - start_time, 2)}s'))
