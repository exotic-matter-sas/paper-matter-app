#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import json
from base64 import b64decode

import filetype
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.http import http_date
from django.views import View
from django_otp.decorators import otp_required
from mptt.exceptions import InvalidMove
from rest_framework import generics, views, serializers, filters
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.errors import get_api_error
from core.models import FTLDocument, FTLFolder
from core.processing.ftl_processing import FTLDocumentProcessing
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer
from ftl.enums import FTLStorages, FTLPlugins

ftl_doc_processing = FTLDocumentProcessing(settings.FTL_DOC_PROCESSING_PLUGINS)


def _extract_binary_from_data_uri(data_uri):
    header, encoded = data_uri.split(",", 1)
    return b64decode(encoded)


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {**SearchQuery.SEARCH_TYPES, 'web': 'websearch_to_tsquery'}

@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class HomeView(View):

    def get(self, request, *args, **kwargs):
        context = {
            'org_name': request.session['org_name'],
            # ftl_account is exposed to javascript through json_script filter in home.html template
            'ftl_account': {'name': request.user.get_username(),  # get_username now return email
                            'isSuperUser': request.user.is_superuser},
        }
        return render(request, 'core/home.html', context)


# API

class DownloadView(views.APIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs['uuid'])

        if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
            return HttpResponseRedirect(doc.binary.url)
        else:
            response = HttpResponse(doc.binary, 'application/octet')
            response['Last-Modified'] = http_date(doc.edited.timestamp())
            response['Content-Disposition'] = f'attachment; filename="{doc.binary.name}"'
            return response


class ViewPDF(DownloadView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'inline'
        return response


class FTLDocumentList(generics.ListAPIView):
    serializer_class = FTLDocumentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created', 'title']

    def get_queryset(self):
        current_folder = self.request.query_params.get('level', None)
        flat_mode = True if self.request.query_params.get('flat', False) is not False else False
        text_search = self.request.query_params.get('search', None)

        queryset = FTLDocument.objects.filter(org=self.request.user.org).order_by('-created')

        if not flat_mode:
            if text_search:
                search_query = WebSearchQuery(text_search.strip(), config=F('language'), search_type='web')

                queryset = queryset.annotate(rank=SearchRank(F('tsvector'), search_query)) \
                    .filter(tsvector=search_query) \
                    .filter(rank__gt=0) \
                    .order_by('-rank')

            elif current_folder is not None and int(current_folder) > 0:
                queryset = queryset.filter(ftl_folder__id=current_folder)
            else:
                queryset = queryset.filter(ftl_folder__isnull=True)

        return queryset


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def perform_update(self, serializer):
        need_processing = False
        force_processing = set()
        if serializer.initial_data and 'title' in serializer.initial_data:
            if serializer.instance.title != serializer.initial_data['title']:
                need_processing = True
                force_processing.add(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR)

        if serializer.initial_data and 'note' in serializer.initial_data:
            if serializer.instance.title != serializer.initial_data['note']:
                need_processing = True
                force_processing.add(FTLPlugins.SEARCH_ENGINE_PGSQL_TSVECTOR)

        instance = serializer.save(org=self.request.user.org)

        if need_processing:
            # only apply processing in case value changed, avoid processing when just moving document in folder
            ftl_doc_processing.apply_processing(instance, list(force_processing))


class FTLDocumentThumbnail(views.APIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs['pid'])

        if not bool(doc.thumbnail_binary):
            return HttpResponseNotFound()

        if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
            return HttpResponseRedirect(doc.thumbnail_binary.url)
        else:
            response = HttpResponse(doc.thumbnail_binary, 'image/png')
            response['Last-Modified'] = http_date(doc.edited.timestamp())
            # TODO add ETAG and last modified for caching
            return response


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer
    # Needed for applying permission checking on view that don't have any queryset
    queryset = FTLDocument.objects.none()

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES or 'json' not in request.POST:
            return HttpResponseBadRequest()

        file_obj = request.FILES['file']

        kind = filetype.guess(file_obj)
        if not kind or kind.mime != "application/pdf":
            return HttpResponseBadRequest()

        payload = json.loads(request.POST['json'])

        if 'ftl_folder' in payload and payload['ftl_folder']:
            try:
                ftl_folder = get_object_or_404(FTLFolder.objects.filter(org=self.request.user.org),
                                               id=payload['ftl_folder'])
            except Http404:
                raise serializers.ValidationError(get_api_error('ftl_folder_not_found'))
        else:
            ftl_folder = None

        with transaction.atomic():
            ftl_doc = FTLDocument()
            ftl_doc.ftl_folder = ftl_folder
            ftl_doc.ftl_user = self.request.user
            ftl_doc.binary = file_obj
            ftl_doc.org = self.request.user.org
            ftl_doc.title = file_obj.name

            if 'created' in payload and payload['created']:
                ftl_doc.created = payload['created']

            if 'thumbnail' in request.POST and request.POST['thumbnail']:
                try:
                    ftl_doc.thumbnail_binary = ContentFile(_extract_binary_from_data_uri(request.POST['thumbnail']),
                                                           'thumb.png')
                except ValueError as e:
                    if 'ignore_thumbnail_generation_error' in payload and \
                        not payload['ignore_thumbnail_generation_error']:
                        raise e
                    else:
                        pass

            ftl_doc.save()

        ftl_doc_processing.apply_processing(ftl_doc, force=[FTLPlugins.LANG_DETECTOR_LANGID])

        return Response(self.serializer_class(ftl_doc).data, status=201)


class FTLFolderList(generics.ListCreateAPIView):
    serializer_class = FTLFolderSerializer
    pagination_class = None

    def get_queryset(self):
        current_folder = self.request.query_params.get('level')

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
            if 'folder_name_unique_for_org_level' in str(e):
                raise serializers.ValidationError(get_api_error('folder_name_unique_for_org_level'))
            else:
                raise


class FTLFolderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLFolderSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return FTLFolder.objects.filter(org=self.request.user.org)

    def perform_update(self, serializer):
        # When detecting `parent` change, call the move_to to handle moving folder in the tree (mptt)
        if serializer.initial_data and 'parent' in serializer.initial_data:
            if serializer.instance.parent != serializer.initial_data['parent']:

                if serializer.initial_data['parent'] is None:
                    # Root
                    serializer.instance.move_to(None)
                else:
                    target_folder = get_object_or_404(self.get_queryset(), id=serializer.initial_data['parent'])
                    try:
                        serializer.instance.move_to(target_folder)
                    except InvalidMove:
                        raise serializers.ValidationError(get_api_error('folder_parent_invalid'))
        try:
            serializer.save(org=self.request.user.org)
        except IntegrityError as e:
            if 'folder_name_unique_for_org_level' in str(e):
                raise serializers.ValidationError(get_api_error('folder_name_unique_for_org_level'))
            else:
                raise
