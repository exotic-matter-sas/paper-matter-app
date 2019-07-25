import time

from django.core.management import BaseCommand
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from core.models import FTLDocument
from core.processing.ftl_processing import FTLDocumentProcessing


class Command(BaseCommand):
    help = 'Reindex all documents'

    def handle(self, *args, **options):
        processing = FTLDocumentProcessing()
        docs = FTLDocument.objects.all()

        start_time = time.time()
        documents_count = len(docs)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                ngettext(
                    'Starting to reindex one document',
                    'Starting to reindex %(count)s documents',
                    documents_count
                ) % {
                    'count': documents_count
                }
            )
        )

        for doc in docs:
            self.stdout.write(
                _('Reindexing %(title)s') % {'title': doc.title}
            )

            processing.apply_processing(doc)

            self.stdout.write(
                self.style.SUCCESS(
                    _('OK')
                )
            )

        # Wait for all processing done
        processing.executor.shutdown(True)

        end_time = time.time()

        self.stdout.write(
            self.style.SUCCESS(
                ngettext(
                    'One document successfully reindexed in %(time)s seconds',
                    '%(count)s documents successfully reindexed in %(time)s seconds',
                    documents_count
                ) % {
                    'count': documents_count,
                    'time': round(end_time - start_time, 2)
                }
            )
        )
