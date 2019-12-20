#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import time

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from core.models import FTLDocument
from core.processing.ftl_processing import FTLDocumentProcessing
from ftl.enums import FTLPlugins


class Command(BaseCommand):
    help = 'Reindex all documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='append',
            help='Force processing for the indicated plugin (can be specified multiple times, plugins list available in'
                 ' ftl.enums.FTLPlugins',
        )

    def handle(self, *args, **options):
        plugins_forced = list()
        if options['force']:
            for plugin in options['force']:
                value = FTLPlugins.get_value(plugin)
                if value:
                    self.stdout.write(
                        self.style.MIGRATE_HEADING(
                            _('Forcing plugin %(value)s') % {'value': value}
                        )
                    )
                    plugins_forced.append(value)

        processing = FTLDocumentProcessing(settings.FTL_DOC_PROCESSING_PLUGINS)
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

            processing.apply_processing(doc, plugins_forced)

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
