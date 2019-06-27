import binascii
from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework import serializers

from core.models import FTLDocument, FTLFolder


class ThumbnailField(serializers.FileField):
    def to_internal_value(self, data):
        header, encoded = data.split(",", 1)
        try:
            binary = b64decode(encoded)
        except binascii.Error:
            self.fail("Could not decode base64 thumbnail")

        return ContentFile(binary, 'thumb.png')


class FTLDocumentSerializer(serializers.ModelSerializer):
    thumbnail_binary = ThumbnailField(write_only=True)
    thumbnail_available = serializers.SerializerMethodField()

    def get_thumbnail_available(self, obj):
        return bool(obj.thumbnail_binary)

    class Meta:
        model = FTLDocument
        fields = ('pid', 'title', 'note', 'created', 'edited', 'ftl_folder', 'thumbnail_binary', 'thumbnail_available')
        read_only_fields = ('created', 'edited', 'thumbnail_available')


class FTLFolderSerializer(serializers.ModelSerializer):
    paths = serializers.SerializerMethodField()

    def get_paths(self, obj):
        return map(lambda e: {'id': e.id, 'name': e.name}, obj.get_ancestors(include_self=True))

    class Meta:
        model = FTLFolder
        fields = ('id', 'name', 'created', 'parent', 'paths')
        read_only_fields = ('created',)
