import json
from base64 import b64decode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.http import http_date
from django.views import View
from rest_framework import generics, views, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.errors import get_api_error
from core.models import FTLDocument, FTLFolder, FTLModelPermissions
from core.processing.ftl_processing import FTLDocumentProcessing
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer
from ftl.constants import FTLStorages

ftl_doc_processing = FTLDocumentProcessing(settings.FTL_DOC_PROCESSING_PLUGINS)


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

        if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
            return HttpResponseRedirect(doc.binary.url)
        else:
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
        text_search = self.request.query_params.get('search', None)

        queryset = FTLDocument.objects.filter(org=self.request.user.org).order_by('-created')

        if not flat_mode:
            if text_search:
                search_query = SearchQuery(text_search.strip(), config=F('language'))
                queryset = queryset.annotate(rank=SearchRank(F('tsvector'), search_query)) \
                    .filter(rank__gte=0.1) \
                    .order_by('-rank')
            elif current_folder is not None and int(current_folder) > 0:
                queryset = queryset.filter(ftl_folder__id=current_folder)
            else:
                queryset = queryset.filter(ftl_folder__isnull=True)

        return queryset


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        return FTLDocument.objects.filter(org=self.request.user.org)

    def perform_update(self, serializer):
        serializer.save(org=self.request.user.org)


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

        if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
            return HttpResponseRedirect(doc.thumbnail_binary.url)
        else:
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

        ftl_doc_processing.apply_processing(ftl_doc)

        return Response(self.serializer_class(ftl_doc).data, status=201)


class FTLFolderList(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLFolderSerializer
    pagination_class = None
    permission_classes = (FTLModelPermissions,)

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
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLFolderSerializer
    lookup_field = 'id'
    permission_classes = (FTLModelPermissions,)

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
                    serializer.instance.move_to(target_folder)
            else:
                serializer.save(org=self.request.user.org)
        else:
            serializer.save(org=self.request.user.org)
