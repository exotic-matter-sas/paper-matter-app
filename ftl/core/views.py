#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import hashlib
import json
import urllib
from base64 import b64decode
from pathlib import Path

import magic
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
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
from rest_framework import generics, views, serializers, filters
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.errors import get_api_error
from core.ftl_mixins import FTLUserContextDataMixin
from core.mimes import mimetype_to_ext
from core.models import FTLDocument, FTLFolder
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer
from core.tasks import apply_ftl_processing
from ftl.enums import FTLStorages, FTLPlugins


def _extract_binary_from_data_uri(data_uri):
    header, encoded = data_uri.split(",", 1)
    return b64decode(encoded)


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {**SearchQuery.SEARCH_TYPES, "web": "websearch_to_tsquery"}


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class HomeView(FTLUserContextDataMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "core/home.html", self.get_context_data())


# API


class DownloadView(views.APIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = "pid"

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org, deleted=False)

    def _get_doc(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs["uuid"])

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
                {"response-content-disposition": "inline"}
            )

            return HttpResponseRedirect(f"{doc.binary.url}&{urlencode}")
        else:
            response = HttpResponse(doc.binary, doc.type)
            response["Content-Disposition"] = "inline"
            return response


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

        return queryset


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = "pid"

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
            ftl_doc_processing.apply_processing(instance, list(force_processing))

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


@method_decorator(transaction.non_atomic_requests, name="dispatch")
class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer
    # Needed for applying permission checking on view that don't have any queryset
    queryset = FTLDocument.objects.none()

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES or "json" not in request.POST:
            return HttpResponseBadRequest()

        file_obj = request.FILES["file"]

        mime = magic.from_buffer(file_obj.read(2048), mime=True)
        extension = mimetype_to_ext(mime)
        if not extension:
            return HttpResponseBadRequest()

        payload = json.loads(request.POST["json"])

        if "ftl_folder" in payload and payload["ftl_folder"]:
            try:
                ftl_folder = get_object_or_404(
                    FTLFolder.objects.filter(org=self.request.user.org),
                    id=payload["ftl_folder"],
                )
            except Http404:
                raise serializers.ValidationError(get_api_error("ftl_folder_not_found"))
        else:
            ftl_folder = None

        with transaction.atomic():
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
                    raise serializers.ValidationError(
                        get_api_error("ftl_document_md5_mismatch")
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
                        raise e
                    else:
                        pass

            ftl_doc.save()

        # ftl_doc_processing.apply_processing(
        #     ftl_doc, force=[FTLPlugins.LANG_DETECTOR_LANGID]
        # )

        apply_ftl_processing.delay(ftl_doc.pk, force=[FTLPlugins.LANG_DETECTOR_LANGID])

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
                raise serializers.ValidationError(
                    get_api_error("folder_name_unique_for_org_level")
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
                        raise serializers.ValidationError(
                            get_api_error("folder_parent_invalid")
                        )
        try:
            serializer.save(org=self.request.user.org)
        except IntegrityError as e:
            if "folder_name_unique_for_org_level" in str(e):
                raise serializers.ValidationError(
                    get_api_error("folder_name_unique_for_org_level")
                )
            else:
                raise
