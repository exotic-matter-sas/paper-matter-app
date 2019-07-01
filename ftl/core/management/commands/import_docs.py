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
    help = 'Mass import documents to FTL'
    user = None

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', type=str)
        parser.add_argument('username', nargs='?', type=str)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                _(
                    'Starting to migrate for %(username)s from %(path)s'
                ) % {
                    'username': options['username'],
                    'path': options['path']
                }
            )
        )

        self.user = FTLUser.objects.get(username=options['username'])

        start_time = time.time()
        count = self._explore(options['path'])
        end_time = time.time()

        self.stdout.write(
            self.style.SUCCESS(
                ngettext(
                    'One document successfully imported in %(time)s',
                    '%(count)s documents successfully imported in %(time)s',
                    count
                ) % {
                    'count': count,
                    'time': round(end_time - start_time, 2)
                }
            )
        )

    def _explore(self, path, ftl_parent_folder=None, count=0):
        current = os.scandir(path)
        _count = count

        for directory in current:
            if directory.is_dir():
                folder = FTLFolder()
                folder.name = directory.name
                folder.parent = ftl_parent_folder
                folder.org = self.user.org
                folder.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        _('Created folder %(name)s') % {'name': directory.name}
                    )
                )

                _count += self._explore(directory.path, folder, count)

            elif directory.is_file():
                file = directory

                if pathlib.Path(file.path).suffix.lower() == '.pdf':
                    self.stdout.write(
                        self.style.SUCCESS(
                            _('Imported document %(name)s') % {'name': file.name}
                        )
                    )

                    with open(file.path, 'rb') as f:
                        document = FTLDocument()
                        document.ftl_folder = ftl_parent_folder
                        document.ftl_user = self.user
                        document.binary = File(f)
                        document.org = self.user.org
                        document.title = file.name
                        document.created = timezone.make_aware(
                            datetime.fromtimestamp(int(os.path.getmtime(file.path))),
                            timezone.get_current_timezone())
                        document.save()
                        _count += 1

        return _count
