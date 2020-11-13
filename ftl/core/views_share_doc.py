#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from datetime import datetime
from pathlib import Path

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic.base import ContextMixin

from core.mimes import mimetype_to_ext
from core.models import FTLDocumentSharing
from core.views import DownloadView


def get_shared_doc(pid):
    now = timezone.now()
    ftl_document_sharing = get_object_or_404(FTLDocumentSharing, pid=pid)
    if ftl_document_sharing.expire_at and ftl_document_sharing.expire_at < now:
        ftl_document_sharing.delete()
        raise Http404()

    return ftl_document_sharing


class ViewSharedDocument(ContextMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            ftl_document_sharing = get_shared_doc(kwargs["pid"])
        except Http404:
            return render(request, "core/share_doc_404.html", status=404)

        context = self.get_context_data()
        context["force_refresh_id"] = int(datetime.utcnow().timestamp())
        context["share_doc"] = ftl_document_sharing
        # remove the dot from extension
        context["doc_ext"] = mimetype_to_ext(ftl_document_sharing.ftl_doc.type)[1:]
        return render(request, "core/share_doc.html", context)


class DownloadSharedDocument(DownloadView):
    authentication_classes = []
    permission_classes = []

    def _get_doc(self, request, *args, **kwargs):
        ftl_document_sharing = get_shared_doc(kwargs["pid"])

        doc_ext = Path(ftl_document_sharing.ftl_doc.binary.name).suffix.lower()

        # Slugify only the filename, not the file extension
        if ftl_document_sharing.ftl_doc.title.lower().endswith(doc_ext):
            title = f"{slugify(ftl_document_sharing.ftl_doc.title[:-len(doc_ext)])[:128]}{doc_ext}"
        else:
            title = f"{slugify(ftl_document_sharing.ftl_doc.title)[:128]}{doc_ext}"

        return ftl_document_sharing.ftl_doc, doc_ext, title
