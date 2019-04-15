from rest_framework import serializers

from core.models import FTLDocument, FTLFolder


class FTLDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTLDocument
        fields = ('pid', 'title', 'note', 'created', 'edited', 'ftl_folder')
        read_only_fields = ('created', 'edited')


class FTLFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTLFolder
        fields = ('id', 'name', 'created', 'parent')
        read_only_fields = ('created', )
