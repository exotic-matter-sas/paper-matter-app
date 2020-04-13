#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
import pathlib
import time
from datetime import datetime

from django.core.files.base import File
from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from core.models import FTLFolder, FTLDocument, FTLUser


class Command(BaseCommand):
    help = "Mass import PDF documents and folder tree to FTL"
    user = None

    def add_arguments(self, parser):
        parser.add_argument("-p", "--path", nargs="?", type=str, required=True)
        parser.add_argument("-u", "--email", nargs="?", type=str, required=True)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                _("Starting mass import for %(email)s from %(path)s")
                % {"email": options["email"], "path": options["path"]}
            )
        )

        self.user = FTLUser.objects.get(email=options["email"])

        start_time = time.time()
        count = self._explore_and_import(options["path"])
        end_time = time.time()

        self.stdout.write(
            self.style.SUCCESS(
                ngettext(
                    "One document successfully imported in %(time)s",
                    "%(count)s documents successfully imported in %(time)s",
                    count,
                )
                % {"count": count, "time": round(end_time - start_time, 2)}
            )
        )

    def _explore_and_import(self, path, ftl_parent_folder=None, count=0):
        items_to_import = os.scandir(path)
        _count = count

        for item in items_to_import:
            if item.is_dir():
                folder = FTLFolder()
                folder.name = item.name
                folder.parent = ftl_parent_folder
                folder.org = self.user.org
                folder.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        _("Created folder %(name)s") % {"name": item.name}
                    )
                )

                _count += self._explore_and_import(item.path, folder, count)

            elif item.is_file():
                file = item

                if pathlib.Path(file.path).suffix.lower() == ".pdf":
                    self.stdout.write(
                        self.style.SUCCESS(
                            _("Imported document %(name)s") % {"name": file.name}
                        )
                    )

                    with open(file.path, "rb") as f:
                        document = FTLDocument()
                        document.ftl_folder = ftl_parent_folder
                        document.ftl_user = self.user
                        document.binary = File(f)
                        document.org = self.user.org
                        document.title = file.name
                        document.created = timezone.make_aware(
                            datetime.fromtimestamp(int(os.path.getmtime(file.path))),
                            timezone.get_current_timezone(),
                        )
                        document.save()
                        _count += 1

        return _count
