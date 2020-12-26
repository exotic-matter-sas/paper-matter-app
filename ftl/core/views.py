#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import hashlib
import json
import urllib
from base64 import b64decode
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner, BadSignature
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    Http404,
)
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.http import http_date
from django.utils.text import slugify
from django.views import View
from django_otp.decorators import otp_required
from mptt.exceptions import InvalidMove
from rest_framework import generics, views, filters
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.errors import ERROR_CODES_DETAILS, BadRequestError
from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin
from core.mimes import mimetype_to_ext, guess_mimetype
from core.models import FTLDocument, FTLFolder, FTLDocumentSharing, FTLDocumentReminder
from core.serializers import (
    FTLDocumentSerializer,
    FTLFolderSerializer,
    FTLDocumentSharingSerializer,
    FTLDocumentDetailsOnlyOfficeSerializer,
    FTLDocumentReminderSerializer,
)
from core.tasks import apply_ftl_processing
from ftl.enums import FTLStorages, FTLPlugins


def _extract_binary_from_data_uri(data_uri):
    header, encoded = data_uri.split(",", 1)
    return b64decode(encoded)


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {**SearchQuery.SEARCH_TYPES, "web": "websearch_to_tsquery"}


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class HomeView(FTLAccountProcessorContextMixin, View):
    def get(self, request, *args, **kwargs):
        return render(
            request, "core/home.html", self.get_ftl_context_data_with_request(request)
        )


# API


class DownloadView(views.APIView):
    serializer_class = None
    lookup_field = "pid"

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org, deleted=False)

    def _get_doc(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs["pid"])

        doc_ext = Path(doc.binary.name).suffix.lower()

        # Slugify only the filename, not the file extension
        if doc.title.lower().endswith(doc_ext):
            title = f"{slugify(doc.title[:-len(doc_ext)])[:128]}{doc_ext}"
        else:
            title = f"{slugify(doc.title)[:128]}{doc_ext}"

        return doc, doc_ext, title

    def get(self, request, *args, **kwargs):
        doc, doc_ext, title = self._get_doc(request, *args, **kwargs)

        if settings.DEFAULT_FILE_STORAGE in [
            FTLStorages.GCS,
        ]:
            urlencode = urllib.parse.urlencode(
                {"response-content-disposition": f'attachment; filename="{title}"'}
            )

            return HttpResponseRedirect(f"{doc.binary.url}&{urlencode}")
        else:
            response = HttpResponse(doc.binary, "application/octet-stream")
            response["Last-Modified"] = http_date(doc.edited.timestamp())
            response["Content-Disposition"] = f'attachment; filename="{title}"'
            return response


class ViewDocument(DownloadView):
    def get(self, request, *args, **kwargs):
        doc, doc_ext, title = self._get_doc(request, *args, **kwargs)

        if settings.DEFAULT_FILE_STORAGE in [
            FTLStorages.GCS,
        ]:
            urlencode = urllib.parse.urlencode(
                {"response-content-disposition": f'inline; filename="{title}"'}
            )

            return HttpResponseRedirect(f"{doc.binary.url}&{urlencode}")
        else:
            response = HttpResponse(doc.binary, doc.type)
            if doc.type == "text/plain":
                response["Content-Type"] = f"text/plain; charset=utf-8"
            else:
                response["Content-Type"] = doc.type

            response["Content-Disposition"] = f'inline; filename="{title}"'
            return response


class TempDownloadView(DownloadView):
    """
    Generate a temporarily signed download url for a document (5 mins expiration) for use with OnlyOffice document
    server. Authentication is not enabled because the document server downloads the document independently.
    """

    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return FTLDocument.objects.filter(deleted=False)

    def _get_doc(self, request, *args, **kwargs):
        value_to_unsign = kwargs["spid"]
        signer = TimestampSigner()
        try:
            pid = signer.unsign(value_to_unsign, max_age=timedelta(minutes=5))
            kwargs["pid"] = pid
            return super()._get_doc(request, *args, **kwargs)
        except BadSignature:
            raise Http404()


class FTLDocumentList(generics.ListAPIView):
    serializer_class = FTLDocumentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created", "title"]

    def get_queryset(self):
        current_folder = self.request.query_params.get("level", None)
        flat_mode = (
            True if self.request.query_params.get("flat", False) is not False else False
        )
        text_search = self.request.query_params.get("search", None)

        queryset = FTLDocument.objects.filter(
            org=self.request.user.org, deleted=False
        ).order_by("-created")

        if not flat_mode:
            if text_search:
                search_query = WebSearchQuery(
                    text_search.strip(), config=F("language"), search_type="web"
                )

                queryset = (
                    queryset.annotate(rank=SearchRank(F("tsvector"), search_query))
                    .filter(tsvector=search_query)
                    .filter(rank__gt=0)
                    .order_by("-rank")
                )

            elif current_folder is not None and int(current_folder) > 0:
                queryset = queryset.filter(ftl_folder__id=current_folder)
            else:
                queryset = queryset.filter(ftl_folder__isnull=True)
        elif current_folder is not None and int(current_folder) > 0:
            # Get list of folders descendent
            folders_qs = FTLFolder.objects.filter(
                org=self.request.user.org, id=current_folder
            ).get_descendants(include_self=True)
            folders_in = [f.id for f in folders_qs]
            queryset = queryset.filter(ftl_folder__in=folders_in)

        return queryset


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "pid"

    def get_serializer_class(self):
        return (
            FTLDocumentDetailsOnlyOfficeSerializer
            if getattr(settings, "FTL_ENABLE_ONLY_OFFICE", False)
            else FTLDocumentSerializer
        )

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org, deleted=False)

    def perform_update(self, serializer):
        need_processing = False
        force_processing = set()
        if serializer.initial_data and "title" in serializer.initial_data:
            if serializer.instance.title != serializer.initial_data["title"]:
                need_processing = True
                force_processing.add(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR)

        if serializer.initial_data and "note" in serializer.initial_data:
            if serializer.instance.title != serializer.initial_data["note"]:
                need_processing = True
                force_processing.add(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR)

        instance = serializer.save(org=self.request.user.org)

        if need_processing:
            # only apply processing in case value changed, avoid processing when just moving document in folder
            transaction.on_commit(
                lambda: apply_ftl_processing.delay(
                    instance.pid,
                    instance.org.pk,
                    instance.ftl_user.pk,
                    force=list(force_processing),
                )
            )

    def perform_destroy(self, instance):
        instance.mark_delete()


class FTLDocumentThumbnail(views.APIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = "pid"

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org, deleted=False)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs["pid"])

        if not bool(doc.thumbnail_binary):
            return HttpResponseNotFound()

        if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
            return HttpResponseRedirect(doc.thumbnail_binary.url)
        else:
            response = HttpResponse(doc.thumbnail_binary, "image/png")
            response["Last-Modified"] = http_date(doc.edited.timestamp())
            # TODO add ETAG and last modified for caching
            return response


class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer
    # Needed for applying permission checking on view that don't have any queryset
    queryset = FTLDocument.objects.none()

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES or "json" not in request.POST:
            raise BadRequestError(
                ERROR_CODES_DETAILS["ftl_missing_file_or_json_in_body"],
                "ftl_missing_file_or_json_in_body",
            )

        file_obj = request.FILES["file"]

        if file_obj.size == 0:
            raise BadRequestError(
                ERROR_CODES_DETAILS["ftl_file_empty"], "ftl_file_empty",
            )

        mime = guess_mimetype(file_obj, filename=file_obj.name)
        extension = mimetype_to_ext(mime)
        if not extension:
            raise UnsupportedMediaType(
                mime,
                ERROR_CODES_DETAILS["ftl_document_type_unsupported"],
                "ftl_document_type_unsupported",
            )

        payload = json.loads(request.POST["json"])

        if "ftl_folder" in payload and payload["ftl_folder"]:
            try:
                ftl_folder = get_object_or_404(
                    FTLFolder.objects.filter(org=self.request.user.org),
                    id=payload["ftl_folder"],
                )
            except Http404:
                raise BadRequestError(
                    ERROR_CODES_DETAILS["ftl_folder_not_found"], "ftl_folder_not_found",
                )
        else:
            ftl_folder = None

        ftl_doc = FTLDocument()
        ftl_doc.ftl_folder = ftl_folder
        ftl_doc.ftl_user = self.request.user
        ftl_doc.binary = file_obj
        ftl_doc.size = file_obj.size
        ftl_doc.type = mime

        md5 = hashlib.md5()
        for data in ftl_doc.binary.chunks():
            md5.update(data)
        ftl_doc.md5 = md5.hexdigest()

        if "md5" in payload and payload["md5"]:
            if payload["md5"] != ftl_doc.md5:
                raise BadRequestError(
                    ERROR_CODES_DETAILS["ftl_document_md5_mismatch"],
                    "ftl_document_md5_mismatch",
                )

        ftl_doc.org = self.request.user.org

        if "title" in payload and payload["title"]:
            ftl_doc.title = payload["title"]
        else:
            if file_obj.name.lower().endswith(extension):
                ftl_doc.title = file_obj.name[: -(len(extension))]
            else:
                ftl_doc.title = file_obj.name

        # The actual name of the file doesn't matter because we use a random UUID. On the contrary, the extension
        # is important.
        ftl_doc.binary.name = f"document{extension}"

        if "created" in payload and payload["created"]:
            ftl_doc.created = payload["created"]

        if "note" in payload and payload["note"]:
            ftl_doc.note = payload["note"]

        if "thumbnail" in request.POST and request.POST["thumbnail"]:
            try:
                ftl_doc.thumbnail_binary = ContentFile(
                    _extract_binary_from_data_uri(request.POST["thumbnail"]),
                    "thumb.png",
                )
            except ValueError as e:
                if (
                    "ignore_thumbnail_generation_error" in payload
                    and not payload["ignore_thumbnail_generation_error"]
                ):
                    raise BadRequestError(
                        ERROR_CODES_DETAILS["ftl_thumbnail_generation_error"],
                        "ftl_thumbnail_generation_error",
                    )
                else:
                    pass

        ftl_doc.save()

        transaction.on_commit(
            lambda: apply_ftl_processing.delay(
                ftl_doc.pid,
                ftl_doc.org.pk,
                ftl_doc.ftl_user.pk,
                force=[FTLPlugins.LANG_DETECTOR_LANGID],
            )
        )

        return Response(self.serializer_class(ftl_doc).data, status=201)


class FTLFolderList(generics.ListCreateAPIView):
    serializer_class = FTLFolderSerializer
    pagination_class = None

    def get_queryset(self):
        current_folder = self.request.query_params.get("level")

        queryset = FTLFolder.objects.filter(org=self.request.user.org)
        if current_folder is not None and int(current_folder) > 0:
            queryset = queryset.filter(parent__id=current_folder)
        else:
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(org=self.request.user.org)
        except IntegrityError as e:
            if "folder_name_unique_for_org_level" in str(e):
                raise BadRequestError(
                    ERROR_CODES_DETAILS["folder_name_unique_for_org_level"],
                    "folder_name_unique_for_org_level",
                )
            else:
                raise


class FTLFolderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLFolderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return FTLFolder.objects.filter(org=self.request.user.org)

    def perform_update(self, serializer):
        # When detecting `parent` change, call the move_to to handle moving folder in the tree (mptt)
        if serializer.initial_data and "parent" in serializer.initial_data:
            if serializer.instance.parent != serializer.initial_data["parent"]:

                if serializer.initial_data["parent"] is None:
                    # Root
                    serializer.instance.move_to(None)
                else:
                    target_folder = get_object_or_404(
                        self.get_queryset(), id=serializer.initial_data["parent"]
                    )
                    try:
                        serializer.instance.move_to(target_folder)
                    except InvalidMove:
                        raise BadRequestError(
                            ERROR_CODES_DETAILS["folder_parent_invalid"],
                            "folder_parent_invalid",
                        )
        try:
            serializer.save(org=self.request.user.org)
        except IntegrityError as e:
            if "folder_name_unique_for_org_level" in str(e):
                raise BadRequestError(
                    ERROR_CODES_DETAILS["folder_name_unique_for_org_level"],
                    "folder_name_unique_for_org_level",
                )
            else:
                raise


class FTLDocumentSharingList(generics.ListCreateAPIView):
    serializer_class = FTLDocumentSharingSerializer
    lookup_field = "pid"
    lookup_url_kwarg = "spid"

    def get_queryset(self):
        get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["pid"],
        )

        return FTLDocumentSharing.objects.filter(
            ftl_doc__org=self.request.user.org,
            ftl_doc__deleted=False,
            ftl_doc__pid=self.kwargs["pid"],
        )

    def perform_create(self, serializer):
        ftl_doc = get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["pid"],
        )
        serializer.save(ftl_doc=ftl_doc)


class FTLDocumentSharingDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentSharingSerializer
    lookup_field = "pid"
    lookup_url_kwarg = "spid"

    def get_queryset(self):
        get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["pid"],
        )

        return FTLDocumentSharing.objects.filter(
            ftl_doc__org=self.request.user.org,
            ftl_doc__deleted=False,
            ftl_doc__pid=self.kwargs["pid"],
        )


class FTLDocumentReminderList(generics.ListCreateAPIView):
    serializer_class = FTLDocumentReminderSerializer
    lookup_url_kwarg = "apid"

    def get_queryset(self):
        doc = get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["dpid"],
        )

        return FTLDocumentReminder.objects.filter(
            ftl_doc_id=doc.id, ftl_user_id=self.request.user.id,
        )

    def perform_create(self, serializer):
        ftl_doc = get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["dpid"],
        )

        if self.get_queryset().count() >= 5:
            raise BadRequestError(
                ERROR_CODES_DETAILS["ftl_too_many_reminders"], "ftl_too_many_reminders",
            )

        serializer.save(ftl_doc=ftl_doc, ftl_user=self.request.user)


class FTLDocumentReminderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentReminderSerializer
    lookup_url_kwarg = "apid"

    def get_queryset(self):
        doc = get_object_or_404(
            FTLDocument,
            org=self.request.user.org,
            deleted=False,
            pid=self.kwargs["dpid"],
        )

        return FTLDocumentReminder.objects.filter(
            ftl_doc_id=doc.id, ftl_user_id=self.request.user.id,
        )
