#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import logging
from http import HTTPStatus

from django.core import management
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.views import View

from core.models import FTLDocument

logger = logging.getLogger(__name__)


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


class CronView(View):
    def _ok(self):
        return HttpResponseNoContent()

    def _fail(self):
        return HttpResponseServerError()

    def _authfail(self):
        return HttpResponseForbidden()

    def get(self, request, *args, **kwargs):
        # Secure request if coming from App Engine
        # (they remove X-header from the source automatically to avoid spoofing)
        # In case we are in a basic deployment, the App Engine header is emulated

        if "X-Appengine-Cron" in request.headers:
            cron = self.handle(request, args, kwargs)

            if cron:
                return self._ok()
            else:
                return self._fail()
        else:
            return self._authfail()

    def handle(self, request, *args, **kwargs):
        return False


class BatchDeleteDocument(CronView):
    def handle(self, request, *args, **kwargs):
        docs_to_delete = FTLDocument.objects.filter(deleted=True)

        for doc in docs_to_delete:
            logger.info(f"Deleting {doc.pid} ...")
            doc.delete()

        return True


class BatchCleanOauthTokens(CronView):
    def handle(self, request, *args, **kwargs):
        management.call_command("cleartokens")

        return True
