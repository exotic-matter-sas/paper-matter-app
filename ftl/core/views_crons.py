#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from http import HTTPStatus

from django.http import HttpResponse, HttpResponseServerError
from django.views import View

from core.models import FTLDocument


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


class CronView(View):

    def _ok(self):
        return HttpResponseNoContent()

    def _fail(self):
        return HttpResponseServerError()

    def get(self, request, *args, **kwargs):
        cron = self.handle(request, args, kwargs)

        if cron:
            return self._ok()
        else:
            return self._fail()

    def handle(self, request, *args, **kwargs):
        return False


class BatchDeleteDocument(CronView):
    def handle(self, request, *args, **kwargs):
        docs_to_delete = FTLDocument.objects.filter(deleted=True)

        for doc in docs_to_delete:
            doc.delete()

        return True
