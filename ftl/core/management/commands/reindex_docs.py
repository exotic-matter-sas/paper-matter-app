#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

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
            "docs_pid",
            nargs="+",
            type=str,
            action="append",
            help='List of pids of documents to be reindexed. Use "*" for all documents (slow).',
        )

        parser.add_argument(
            "--only-missing-search",
            action="store_true",
            help="Filter on documents which are missing search data",
        )

        parser.add_argument(
            "--force",
            action="append",
            help="Force processing for the indicated plugin (can be specified multiple times, plugins list available in"
            " ftl.enums.FTLPlugins",
        )

    def handle(self, *args, **options):
        pids = options["docs_pid"][0]
        all_docs = "*" in pids

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

        query = FTLDocument.objects.filter(deleted=False)

        if options["only_missing_search"]:
            self.stdout.write(self.style.MIGRATE_HEADING("Only missing search data"))
            query = query.filter(
                tsvector__iexact=""
            )  # Using default "=" operator result in an incorrect tsvector search query

        if all_docs:
            self.stdout.write(self.style.MIGRATE_HEADING("Reindexing ALL docs (slow)"))
        else:
            self.stdout.write(
                self.style.MIGRATE_HEADING(f"Reindexing docs: {','.join(pids)}")
            )
            query = query.filter(pid__in=pids)

        docs = query

        start_time = time.time()
        documents_count = len(docs)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                ngettext(
                    "One document to be reindexed",
                    "%(count)s documents to be reindexed",
                    documents_count,
                )
                % {"count": documents_count}
            )
        )

        for doc in docs:
            self.stdout.write(
                _("Submitted for reindexing %(title)s") % {"title": doc.title}
            )
            apply_ftl_processing.delay(
                doc.pid, doc.org.pk, doc.ftl_user.pk, force=plugins_forced
            )
            self.stdout.write(self.style.SUCCESS(_("OK")))

        end_time = time.time()

        self.stdout.write(
            self.style.SUCCESS(
                ngettext(
                    "One document successfully submitted for reindexing in %(time)s seconds",
                    "%(count)s documents successfully submitted for reindexing in %(time)s seconds",
                    documents_count,
                )
                % {"count": documents_count, "time": round(end_time - start_time, 2)}
            )
        )
