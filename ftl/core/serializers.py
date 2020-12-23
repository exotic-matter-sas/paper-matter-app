#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import binascii
from base64 import b64decode

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.utils.translation import get_language_from_request
from jose import jwt
from rest_framework import serializers

from core.mimes import mimetype_to_ext
from core.models import FTLDocument, FTLFolder, FTLDocumentSharing, FTLDocumentAlert
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
        return reverse("api_download_url", kwargs={"pid": obj.pid})

    def get_is_shared(self, obj):
        return obj.share_pids.count() > 0

    class Meta:
        model = FTLDocument
        fields = [
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
            "alerts",
        ]
        read_only_fields = [
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
        ]


class FTLDocumentDetailsOnlyOfficeSerializer(FTLDocumentSerializer):
    only_office_config = serializers.SerializerMethodField()

    def get_download_url_temp(self, obj):
        signer = TimestampSigner()
        value = signer.sign(obj.pid)

        request = self.context.get("request", None)
        relative_url = reverse("api_temp_download_url", kwargs={"spid": value})

        if request:
            return request.build_absolute_uri(relative_url)

        return f"{getattr(settings, 'FTL_EXTERNAL_HOST')}{relative_url}"

    def get_only_office_config(self, obj):
        if obj.type in getattr(
            settings, "FTL_ONLY_OFFICE_SUPPORTED_DOCUMENTS_TYPES", []
        ):
            request = self.context.get("request", None)
            if request:
                current_lang = get_language_from_request(request)
            else:
                current_lang = "en"

            only_office_config = {
                "document": {
                    "fileType": mimetype_to_ext(obj.type)[1:],
                    "key": str(obj.pid),
                    "title": obj.title,
                    "url": self.get_download_url_temp(obj),
                    "permissions": {
                        "comment": False,
                        "copy": True,
                        "download": True,
                        "edit": False,
                        "fillForms": False,
                        "modifyContentControl": False,
                        "modifyFilter": False,
                        "print": True,
                        "review": False,
                    },
                },
                "editorConfig": {
                    "lang": current_lang,
                    "mode": "view",
                    "customization": {
                        "autosave": False,
                        "chat": False,
                        "commentAuthorOnly": False,
                        "comments": False,
                        "compactHeader": False,
                        "compactToolbar": False,
                        "compatibleFeatures": False,
                        "help": True,
                        "hideRightMenu": False,
                        "mentionShare": False,
                        "plugins": False,
                        "reviewDisplay": "original",
                        "showReviewChanges": False,
                        "spellcheck": False,
                        "toolbarNoTabs": False,
                        "unit": "cm",
                        "zoom": -2,
                    },
                },
            }

            only_office_config["token"] = jwt.encode(
                only_office_config,
                getattr(settings, "FTL_ONLY_OFFICE_SECRET_KEY"),
                algorithm="HS256",
            )

            return only_office_config
        else:
            return None

    class Meta(FTLDocumentSerializer.Meta):
        fields = FTLDocumentSerializer.Meta.fields + [
            "only_office_config",
        ]
        read_only_fields = FTLDocumentSerializer.Meta.read_only_fields + [
            "only_office_config",
        ]


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

        return f"{getattr(settings, 'FTL_EXTERNAL_HOST')}{relative_url}"

    class Meta:
        model = FTLDocumentSharing
        fields = ("pid", "created", "edited", "expire_at", "note", "public_url")
        read_only_fields = ("pid", "created", "edited", "public_url")


class FTLDocumentAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTLDocumentAlert
        fields = ("id", "alert_on", "note")
        read_only_fields = ("id",)
