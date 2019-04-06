import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import generics, views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import FTLDocument, FTLFolder
from core.serializers import FTLDocumentSerializer, FTLFolderSerializer


@login_required
def home(request):
    context = {
        'org_name': request.session['org_name'],
        'username': request.user.get_username(),
    }
    return render(request, 'core/home.html', context)


class DownloadView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(FTLDocument.objects.filter(ftl_user=self.request.user, pid=kwargs['uuid']))
        response = HttpResponse(doc.binary, 'application/octet')
        response['Content-Disposition'] = 'attachment; filename="%s"' % doc.binary.name
        return response


class FTLDocumentList(generics.ListCreateAPIView):
    serializer_class = FTLDocumentSerializer

    def get_queryset(self):
        current_folder = self.request.query_params.get('level', None)

        queryset = FTLDocument.objects.filter(ftl_user=self.request.user)

        if current_folder is not None:
            queryset = queryset.filter(ftl_folder__id=current_folder)

        return queryset

    def perform_create(self, serializer):
        serializer.save()  # TODO Do we need this?


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentSerializer
    lookup_field = 'pid'

    def get_queryset(self):
        return FTLDocument.objects.filter(ftl_user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pid=self.kwargs['pid'])

    def perform_update(self, serializer):
        serializer.save(ftl_user=self.request.user)

    def perform_destroy(self, instance):
        binary = instance.binary
        super().perform_destroy(instance)
        binary.file.close()
        os.remove(binary.file.name)


class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FTLDocumentSerializer

    def post(self, request):
        file_obj = request.data['file']
        json = request.data['json']  # Nothing for now

        # TODO check for empty form

        ftl_doc = FTLDocument()
        # ftl_doc.ftl_folder = json['ftl_folder'] or None
        ftl_doc.ftl_user = self.request.user
        ftl_doc.binary = file_obj
        ftl_doc.org = self.request.user.org
        ftl_doc.title = file_obj.name
        ftl_doc.save()

        return Response(self.serializer_class(ftl_doc).data, status=200)


class FTLFolderList(generics.ListCreateAPIView):
    serializer_class = FTLFolderSerializer
    pagination_class = None

    def get_queryset(self):
        current_folder = self.request.query_params.get('level', None)

        queryset = FTLFolder.objects.filter(org=self.request.user.org)
        if current_folder is not None:
            queryset = queryset.filter(parent__id=current_folder)

        return queryset

    def perform_create(self, serializer):
        serializer.save(org=self.request.user.org)
