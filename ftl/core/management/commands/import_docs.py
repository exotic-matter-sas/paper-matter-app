import os
import pathlib
from datetime import datetime

from django.core.files.base import File
from django.core.management import BaseCommand
from django.utils import timezone

from core.models import FTLFolder, FTLDocument, FTLUser


class Command(BaseCommand):
    help = 'Mass import documents to FTL'
    user = None

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', type=str)
        parser.add_argument('username', nargs='?', type=str)

    def handle(self, *args, **options):
        self.user = FTLUser.objects.get(username=options['username'])
        self._explore(options['path'])

    def _explore(self, path, ftl_parent_folder=None):
        current = os.scandir(path)

        for directory in current:
            if directory.is_dir():
                print("dir", directory.name)

                folder = FTLFolder()
                folder.name = directory.name
                folder.parent = ftl_parent_folder
                folder.org = self.user.org
                folder.save()

                self._explore(directory.path, folder)

            elif directory.is_file():
                file = directory

                if pathlib.Path(file.path).suffix.lower() == '.pdf':
                    print("file", file.name)

                    with open(file.path, 'rb') as f:
                        document = FTLDocument()
                        document.ftl_folder = ftl_parent_folder
                        document.ftl_user = self.user
                        document.binary = File(f)
                        document.org = self.user.org
                        document.title = file.name
                        document.created = timezone.make_aware(datetime.fromtimestamp(int(os.path.getmtime(file.path))),
                                                               timezone.get_current_timezone())
                        document.save()
