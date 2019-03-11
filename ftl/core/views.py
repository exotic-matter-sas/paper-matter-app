from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import FTLDocument
from core.serializers import FTLDocumentSerializer


@login_required
def home(request):
    context = {
        'org_name': request.session['org_name'],
        'username': request.user.get_username(),
    }
    return render(request, 'core/home.html', context)


class FTLDocumentList(generics.ListCreateAPIView):
    serializer_class = FTLDocumentSerializer

    def get_queryset(self):
        return FTLDocument.objects.filter(ftl_user__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()  # TODO


class FTLDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FTLDocumentSerializer

    def get_queryset(self):
        return FTLDocument.objects.filter(ftl_user__user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()  # TODO


class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        file_obj = request.data['file']
        title = request.data['name']
        # TODO
        return Response(status=204)

# class FTLDocumentViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = FTLDocument.objects.all()
#     serializer_class = FTLDocumentSerializer

# class FTLOrgViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = FTLOrg.objects.all()
#     serializer_class = FTLOrgSerializer
#
#
# class FTLUserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = FTLUser.objects.all()
#     serializer_class = FTLUserSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
