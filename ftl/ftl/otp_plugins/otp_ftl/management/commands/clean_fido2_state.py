from django.core.management import BaseCommand
from django.utils.translation import ngettext

from ftl.otp_plugins.otp_ftl.models import Fido2State


class Command(BaseCommand):
    help = 'Clean FIDO2 state table'

    def handle(self, *args, **options):
        nb, _ = Fido2State.objects.all().delete()

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                ngettext(
                    'Deleted one state',
                    'Deleted %(count)s states',
                    nb
                ) % {
                    'count': nb
                }
            )
        )
