import json
import os

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import generics, views
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import FTLDocument, FTLFolder, FTLModelPermissions
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer


class HomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'org_name': request.session['org_name'],
            'username': request.user.get_username(),
        }
        return render(request, 'core/home.html', context)


class DownloadView(LoginRequiredMixin, PermissionRequiredMixin, View):
    http_method_names = ['get']
    permission_required = ('core.view_ftldocument',)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(FTLDocument.objects.filter(ftl_user=self.request.user, pid=kwargs['uuid']))
        response = HttpResponse(doc.binary, 'application/octet')
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.binary.name
        return response


class FTLDocumentList(generics.ListAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = FTLDocumentSerializer
    permission_classes = (FTLModelPermissions,)

    def get_queryset(self):
        current_folder = self.request.query_params.get('level', None)

        queryset = FTLDocument.objects.filter(ftl_user=self.request.user).order_by('-created')

        if current_folder is not None:
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
        return FTLDocument.objects.filter(ftl_user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pid=self.kwargs['pid'])

    def perform_update(self, serializer):
        serializer.save(ftl_user=self.request.user)

    def perform_destroy(self, instance):
        if instance.org == self.request.user.org:
            binary = instance.binary
            super().perform_destroy(instance)
            binary.file.close()
            os.remove(binary.file.name)
        else:
            raise ValidationError("Trying to delete document from wrong user!")


class FileUploadView(LoginRequiredMixin, views.APIView):
    authentication_classes = (SessionAuthentication,)
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer
    permission_classes = (FTLModelPermissions,)
    # Needed for applying permission checking on view that don't have any queryset
    queryset = FTLDocument.objects.none()

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        payload = json.loads(request.data['json'])

        # TODO check for empty form

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
        ftl_doc.save()

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
