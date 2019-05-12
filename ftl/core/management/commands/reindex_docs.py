import time

import tika
from django.contrib.postgres.search import SearchVector
from django.core.management import BaseCommand
from tika import parser

from core.models import FTLDocument


class Command(BaseCommand):
    help = 'Reindex all documents'
    vector = SearchVector('content_text', weight='C', config='french') \
             + SearchVector('note', weight='B', config='french') \
             + SearchVector('title', weight='A', config='french')

    def handle(self, *args, **options):
        docs = FTLDocument.objects.all()
        tika.initVM()

        start_time = time.time()
        documents_count = len(docs)
        s = "s" if documents_count > 1 else ""
        self.stdout.write(self.style.MIGRATE_HEADING(f'Starting to reindex {documents_count} document{s}'))

        for doc in docs:
            parsed = parser.from_file(doc.binary.name)
            doc.content_text = parsed["content"].strip()
            doc.save()
            doc.tsvector = self.vector
            doc.save()

            self.stdout.write(self.style.SUCCESS(f'Reindexed {doc.title}'))
        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(f'{documents_count } document{s} successfully reindexed in'
                                             f' {round(end_time-start_time, 2)}s'))
