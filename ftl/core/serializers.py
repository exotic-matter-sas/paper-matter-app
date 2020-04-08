#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import binascii
from base64 import b64decode

from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework import serializers

from core.models import FTLDocument, FTLFolder
from ftl.enums import FTLStorages


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
    thumbnail_url = serializers.SerializerMethodField()
    is_processed = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    def get_thumbnail_available(self, obj):
        return bool(obj.thumbnail_binary)

    def get_thumbnail_url(self, obj):
        if bool(obj.thumbnail_binary):
            if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
                return obj.thumbnail_binary.url
            else:
                return reverse('api_thumbnail_url', kwargs={'pid': obj.pid})
        else:
            return None

    def get_is_processed(self, obj):
        return bool(obj.tsvector)

    def get_path(self, obj):
        if obj.ftl_folder:
            return map(lambda e: {'id': e.id, 'name': e.name}, obj.ftl_folder.get_ancestors(include_self=True))
        else:
            return []

    class Meta:
        model = FTLDocument
        fields = ('pid', 'title', 'note', 'created', 'edited', 'ftl_folder', 'thumbnail_binary', 'thumbnail_available',
                  'thumbnail_url', 'is_processed', 'path', 'md5', 'size', 'ocrized')
        read_only_fields = ('pid', 'created', 'edited', 'thumbnail_available', 'thumbnail_url', 'is_processed', 'path',
                            'size', 'ocrized')


class FTLFolderSerializer(serializers.ModelSerializer):
    paths = serializers.SerializerMethodField()
    has_descendant = serializers.SerializerMethodField()

    def get_paths(self, obj):
        return map(lambda e: {'id': e.id, 'name': e.name}, obj.get_ancestors(include_self=True))

    def get_has_descendant(self, obj):
        return obj.get_descendant_count() > 0

    class Meta:
        model = FTLFolder
        fields = ('id', 'name', 'created', 'parent', 'paths', 'has_descendant')
        read_only_fields = ('created', 'has_descendant')
