#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import logging
from http import HTTPStatus

from django.http import HttpResponse

from core.models import FTLOrg, FTLDocument, FTLFolder
from core.views_crons import CronView

logger = logging.getLogger(__name__)


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


class BatchDeleteOrg(CronView):
    def handle(self, request, *args, **kwargs):
        orgs_to_delete = FTLOrg.objects.filter(deleted=True)

        for org in orgs_to_delete:
            docs = FTLDocument.objects.filter(org=org).exists()
            folders = FTLFolder.objects.filter(org=org).exists()

            if docs or folders:
                logger.info(f"Skipping {org}")
            else:
                logger.info(f"Deleting {org} ...")
                org.delete()

        return True
