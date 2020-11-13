#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import binascii
from base64 import b64decode

from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework import serializers

from core.mimes import mimetype_to_ext
from core.models import FTLDocument, FTLFolder, FTLDocumentSharing
from ftl.enums import FTLStorages


class ThumbnailField(serializers.FileField):
    def to_internal_value(self, data):
        header, encoded = data.split(",", 1)
        try:
            binary = b64decode(encoded)
        except binascii.Error:
            self.fail("Could not decode base64 thumbnail")

        return ContentFile(binary, "thumb.png")


class FTLDocumentSerializer(serializers.ModelSerializer):
    thumbnail_binary = ThumbnailField(write_only=True)
    thumbnail_available = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    is_processed = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    ext = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()

    def get_thumbnail_available(self, obj):
        return bool(obj.thumbnail_binary)

    def get_thumbnail_url(self, obj):
        if bool(obj.thumbnail_binary):
            if settings.DEFAULT_FILE_STORAGE in [FTLStorages.GCS, FTLStorages.AWS_S3]:
                return obj.thumbnail_binary.url
            else:
                return reverse("api_thumbnail_url", kwargs={"pid": obj.pid})
        else:
            return None

    def get_is_processed(self, obj):
        return bool(obj.tsvector)

    def get_path(self, obj):
        if obj.ftl_folder:
            return map(
                lambda e: {"id": e.id, "name": e.name},
                obj.ftl_folder.get_ancestors(include_self=True),
            )
        else:
            return []

    def get_ext(self, obj):
        return mimetype_to_ext(obj.type)

    def get_download_url(self, obj):
        return reverse("api_download_url", kwargs={"uuid": obj.pid})

    def get_is_shared(self, obj):
        return obj.share_pids.count() > 0

    class Meta:
        model = FTLDocument
        fields = (
            "pid",
            "title",
            "note",
            "created",
            "edited",
            "ftl_folder",
            "thumbnail_binary",
            "thumbnail_available",
            "thumbnail_url",
            "is_processed",
            "path",
            "md5",
            "size",
            "ocrized",
            "type",
            "ext",
            "download_url",
            "is_shared",
        )
        read_only_fields = (
            "pid",
            "created",
            "edited",
            "thumbnail_available",
            "thumbnail_url",
            "is_processed",
            "path",
            "size",
            "ocrized",
            "type",
            "ext",
            "download_url",
            "is_shared",
        )


class FTLFolderSerializer(serializers.ModelSerializer):
    paths = serializers.SerializerMethodField()
    has_descendant = serializers.SerializerMethodField()

    def get_paths(self, obj):
        return map(
            lambda e: {"id": e.id, "name": e.name}, obj.get_ancestors(include_self=True)
        )

    def get_has_descendant(self, obj):
        return obj.get_descendant_count() > 0

    class Meta:
        model = FTLFolder
        fields = ("id", "name", "created", "parent", "paths", "has_descendant")
        read_only_fields = ("created", "has_descendant")


class FTLDocumentSharingSerializer(serializers.ModelSerializer):
    public_url = serializers.SerializerMethodField()

    def get_public_url(self, obj):
        request = self.context.get("request", None)
        relative_url = reverse("view_sharing_doc", kwargs={"pid": obj.pid})

        if request:
            return request.build_absolute_uri(relative_url)

        return relative_url

    class Meta:
        model = FTLDocumentSharing
        fields = ("pid", "created", "edited", "expire_at", "note", "public_url")
        read_only_fields = ("pid", "created", "edited", "public_url")
