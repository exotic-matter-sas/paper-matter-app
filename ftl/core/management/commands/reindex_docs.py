import time

from django.core.management import BaseCommand
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from core.models import FTLDocument
from core.views import _extract_text_from_pdf, SEARCH_VECTOR


class Command(BaseCommand):
    help = 'Reindex all documents'

    def handle(self, *args, **options):
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
            _extract_text_from_pdf(SEARCH_VECTOR, doc)

            self.stdout.write(
                self.style.SUCCESS(
                    _('Reindexed %(title)s') % {'title': doc.title}
                )
            )

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
