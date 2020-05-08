#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import time

from django.core.management import BaseCommand
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from core.models import FTLDocument
from core.tasks import apply_ftl_processing
from ftl.enums import FTLPlugins


class Command(BaseCommand):
    help = "Reindex all documents"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="append",
            help="Force processing for the indicated plugin (can be specified multiple times, plugins list available in"
            " ftl.enums.FTLPlugins",
        )

    def handle(self, *args, **options):
        plugins_forced = list()
        if options["force"]:
            for plugin in options["force"]:
                value = FTLPlugins.get_value(plugin)
                if value:
                    self.stdout.write(
                        self.style.MIGRATE_HEADING(
                            _("Forcing plugin %(value)s") % {"value": value}
                        )
                    )
                    plugins_forced.append(value)

        docs = FTLDocument.objects.filter(deleted=False).all()

        start_time = time.time()
        documents_count = len(docs)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                ngettext(
                    "Starting to reindex one document",
                    "Starting to reindex %(count)s documents",
                    documents_count,
                )
                % {"count": documents_count}
            )
        )

        for doc in docs:
            self.stdout.write(_("Reindexing %(title)s") % {"title": doc.title})
            apply_ftl_processing.delay(doc.pk, force=plugins_forced)
            self.stdout.write(self.style.SUCCESS(_("OK")))

        end_time = time.time()

        self.stdout.write(
            self.style.SUCCESS(
                ngettext(
                    "One document successfully reindexed in %(time)s seconds",
                    "%(count)s documents successfully reindexed in %(time)s seconds",
                    documents_count,
                )
                % {"count": documents_count, "time": round(end_time - start_time, 2)}
            )
        )
