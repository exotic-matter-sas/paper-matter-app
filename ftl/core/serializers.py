from rest_framework import serializers

from core.models import FTLDocument


class FTLDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTLDocument
        fields = ('pid', 'title', 'note', 'created', 'edited', 'ftl_folder')
        read_only_fields = ('created', 'edited')
