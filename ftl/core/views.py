import json
import os
from base64 import b64decode
from concurrent.futures.thread import ThreadPoolExecutor

import langid
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.files.base import ContentFile
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils.http import http_date
from django.views import View
from rest_framework import generics, views
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from tika import parser

from core.models import FTLDocument, FTLFolder, FTLModelPermissions
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer

SEARCH_VECTOR = SearchVector('content_text', weight='C', config=F('language')) \
                + SearchVector('note', weight='B', config=F('language')) \
                + SearchVector('title', weight='A', config=F('language'))
COUNTRY_CODE_INDEX = {
    'fr': 'french',
    'en': 'english',
}
EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ftl_indexation_worker")


def _extract_text_from_pdf(vector, ftl_doc_instance):
    parsed_txt = parser.from_file(ftl_doc_instance.binary.name)
    ftl_doc_instance.content_text = parsed_txt["content"].strip()
    ftl_doc_instance.language = COUNTRY_CODE_INDEX.get(langid.classify(ftl_doc_instance.content_text)[0], 'english')
    ftl_doc_instance.save()  # Need to save in actual DB before computing the tsvector
    ftl_doc_instance.tsvector = vector
    ftl_doc_instance.save()


def _extract_binary_from_data_uri(data_uri):
    header, encoded = data_uri.split(",", 1)
    return b64decode(encoded)


class HomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'org_name': request.session['org_name'],
            'ftl_account': {'name': request.user.get_username()},
        }
        return render(request, 'core/home.html', context)


class DownloadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    http_method_names = ['get']
    permission_required = ('core.view_ftldocument',)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(FTLDocument.objects.filter(org=self.request.user.org, pid=kwargs['uuid']))
        response = HttpResponse(doc.binary, 'application/octet')
        response['Last-Modified'] = http_date(doc.edited.timestamp())
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.binary.name
        return response


class FTLDocumentList(generics.ListAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLDocumentSerializer
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        current_folder = self.request.query_params.get('level', None)
        flat_mode = self.request.query_params.get('flat', False)

        queryset = FTLDocument.objects.filter(org=self.request.user.org).order_by('-created')

        if not flat_mode:
            if current_folder is not None:
                queryset = queryset.filter(ftl_folder__id=current_folder)
            else:
                queryset = queryset.filter(ftl_folder__isnull=True)

        text_search = self.request.query_params.get('search')

        if text_search:
            search_query = SearchQuery(text_search.strip(), config=F('language'))
            queryset = queryset.annotate(rank=SearchRank(F('tsvector'), search_query)) \
                .filter(rank__gte=0.1) \
                .order_by('-rank')

        return queryset


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pid=self.kwargs['pid'])

    def perform_update(self, serializer):
        serializer.save(ftl_user=self.request.user)

    def perform_destroy(self, instance):
        if instance.org == self.request.user.org:
            binary = instance.binary
            thumbnail_binary = instance.thumbnail_binary
            super().perform_destroy(instance)

            binary.file.close()
            os.remove(binary.file.name)

            if thumbnail_binary:
                thumbnail_binary.file.close()
                os.remove(thumbnail_binary.file.name)
        else:
            raise ValidationError("Trying to delete document from wrong user!")


class FTLDocumentThumbnail(LoginRequiredMixin, views.APIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(self.get_queryset(), pid=kwargs['pid'])

        if not bool(doc.thumbnail_binary):
            return HttpResponseNotFound()

        response = HttpResponse(doc.thumbnail_binary, 'image/png')
        response['Last-Modified'] = http_date(doc.edited.timestamp())
        # TODO add ETAG and last modified for caching
        return response


class FileUploadView(LoginRequiredMixin, views.APIView):
    authentication_classes = (SessionAuthentication,)
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer
    permission_classes = (FTLModelPermissions,)
    # Needed for applying permission checking on view that don't have any queryset
    queryset = FTLDocument.objects.none()

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES or 'json' not in request.POST:
            return HttpResponseBadRequest()

        file_obj = request.FILES['file']
        payload = json.loads(request.POST['json'])

        if 'ftl_folder' in payload:
            ftl_folder = get_object_or_404(FTLFolder.objects.filter(org=self.request.user.org),
                                           id=payload['ftl_folder'])
        else:
            ftl_folder = None

        ftl_doc = FTLDocument()
        ftl_doc.ftl_folder = ftl_folder
        ftl_doc.ftl_user = self.request.user
        ftl_doc.binary = file_obj
        ftl_doc.org = self.request.user.org
        ftl_doc.title = file_obj.name

        if 'thumbnail' in request.POST:
            ftl_doc.thumbnail_binary = ContentFile(_extract_binary_from_data_uri(request.POST['thumbnail']),
                                                   'thumb.png')

        ftl_doc.save()

        EXECUTOR.submit(_extract_text_from_pdf, SEARCH_VECTOR, ftl_doc)

        return Response(self.serializer_class(ftl_doc).data, status=201)


class FTLFolderList(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLFolderSerializer
    pagination_class = None
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        current_folder = self.request.query_params.get('level')

        queryset = FTLFolder.objects.filter(org=self.request.user.org)
        if current_folder is not None:
            queryset = queryset.filter(parent__id=current_folder)
        else:
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def perform_create(self, serializer):
        serializer.save(org=self.request.user.org)


class FTLFolderDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLFolderSerializer
    lookup_field = 'id'
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        return FTLFolder.objects.filter(org=self.request.user.org)

    def perform_update(self, serializer):
        serializer.save(org=self.request.user.org)

    def perform_destroy(self, instance):
        if instance.org == self.request.user.org:
            instance.delete()
        else:
            raise ValidationError('Trying to delete a folder from wrong user!')
