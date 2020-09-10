#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import hashlib
import logging
import pathlib
import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, AbstractUser, Permission
from django.contrib.postgres.fields.citext import CICharField
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import UniqueConstraint, Q, ForeignKey
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from rest_framework.permissions import DjangoModelPermissions

from ftl import celery
from ftl.enums import FTLStorages

logger = logging.getLogger(__name__)

FTL_PERMISSIONS_USER = [
    "core.add_ftldocument",
    "core.change_ftldocument",
    "core.delete_ftldocument",
    "core.view_ftldocument",
    "core.add_ftlfolder",
    "core.change_ftlfolder",
    "core.delete_ftlfolder",
    "core.view_ftlfolder",
    "core.add_ftldocumentsharing",
    "core.change_ftldocumentsharing",
    "core.delete_ftldocumentsharing",
    "core.view_ftldocumentsharing",
]


def _get_name_binary(instance, filename):
    return "uploads/" + str(uuid.uuid4()) + pathlib.Path(instance.binary.name).suffix


def _get_name_thumb(instance, filename):
    return "uploads/" + str(uuid.uuid4()) + pathlib.Path(filename).suffix


def email_hash_validator(email):
    h = hashlib.md5()
    h.update(email.encode("utf-8"))

    if FTLUser.objects.filter(
        email=f"{h.hexdigest()}{settings.FTL_SUFFIX_DELETED_ACCOUNT}"
    ).exists():
        raise ValidationError(_("This email can't be used."), "used_before")


def org_hash_validator(org_slug):
    h = hashlib.md5()
    h.update(org_slug.encode("utf-8"))

    if FTLOrg.objects.filter(
        slug=f"{h.hexdigest()}{settings.FTL_SUFFIX_DELETED_ORG}"
    ).exists():
        raise ValidationError(_("This organization can't be used."), "used_before")


# FTP orgs
class FTLOrg(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(
        max_length=128, unique=True, validators=[org_hash_validator]
    )  # URL of the org (unique auto create an index)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# custom FTL users Manager (no more username required)
class FTLUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email, is_staff=is_staff, is_superuser=is_superuser, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)


# FTL users
class FTLUser(AbstractUser):
    email_validator = EmailValidator()

    org = models.ForeignKey("FTLOrg", on_delete=models.CASCADE)
    username = models.CharField(
        _("username"),
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={"unique": _("A user with that username already exists."),},
    )
    # override email field to set non blank and unique constrains
    email = models.EmailField(
        _("email address"),
        max_length=256,
        blank=False,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[email_validator, email_hash_validator],
        error_messages={"unique": _("A user with that email already exists."),},
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["org"]

    objects = FTLUserManager()

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Email the user asynchronously
        """
        # Manual call because of mutual import of FTLDocument
        celery.app.send_task(
            "core.tasks.send_email_async",
            args=[subject, message, from_email, [self.email]],
            kwargs=kwargs,
        )


# FTL Documents
class FTLDocument(models.Model):
    pid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)

    org = models.ForeignKey("FTLOrg", on_delete=models.PROTECT, db_index=True)
    ftl_user = models.ForeignKey("FTLUser", on_delete=models.PROTECT)
    ftl_folder = TreeForeignKey(
        "FTLFolder", on_delete=models.PROTECT, null=True, blank=True, db_index=True
    )
    title = models.TextField()
    note = models.TextField(blank=True)
    content_text = models.TextField(blank=True)
    count_pages = models.IntegerField(null=True, blank=True)
    binary = models.FileField(upload_to=_get_name_binary, max_length=256, null=True)
    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(auto_now=True)
    tsvector = SearchVectorField(blank=True)
    language = models.CharField(max_length=64, default="simple")
    thumbnail_binary = models.FileField(
        upload_to=_get_name_thumb, max_length=256, null=True
    )
    size = models.BigIntegerField(default=0)
    md5 = models.CharField(max_length=32, null=True)
    deleted = models.BooleanField(default=False)
    ocrized = models.BooleanField(default=False)
    ocr_retry = models.IntegerField(default=0)
    type = models.CharField(max_length=255, default="application/pdf")

    class Meta:
        indexes = [
            models.Index(fields=["org", "pid"]),
            models.Index(fields=["org", "ftl_folder"]),
            # TODO tsvector index missing
            # GinIndex(fields=['tsvector']),
        ]

    def __str__(self):
        return str(self.pid)

    def mark_delete(self, async_delete=True, *args, **kwargs):
        self.deleted = True
        self.ftl_folder = None
        self.save()

        # We send the task manually instead of calling `core.tasks.delete_document`
        # because of mutual import of FTLDocument
        if async_delete:
            celery.app.send_task(
                "core.tasks.delete_document",
                args=[self.pid, self.org.pk, self.ftl_user.pk],
            )

    def delete(self, *args, **kwargs):
        """Override to ensure document file is deleted"""

        binary = self.binary
        thumbnail_binary = self.thumbnail_binary

        if binary:
            try:
                binary.delete(False)
            except Exception as e:
                # except is very broad but it can be anything depending of the storage backend

                # Django FILE_SYSTEM storage doesn't raise an exception if file doesn't exist
                # https://docs.djangoproject.com/en/3.0/ref/files/storage/#django.core.files.storage.FileSystemStorage.directory_permissions_mode
                # AWS_S3 storage doesn't raise an exception if file doesn't exist
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.delete
                if settings.DEFAULT_FILE_STORAGE == FTLStorages.GCS:
                    from google.cloud.exceptions import NotFound

                    if isinstance(e, NotFound):
                        logger.warning("Missing binary in storage backend", e)
                        pass
                    else:
                        raise
                else:
                    raise

        if thumbnail_binary:
            try:
                thumbnail_binary.delete(False)
            except Exception as e:
                if settings.DEFAULT_FILE_STORAGE == FTLStorages.GCS:
                    from google.cloud.exceptions import NotFound

                    if isinstance(e, NotFound):
                        logger.warning("Missing binary in storage backend", e)
                        pass
                    else:
                        raise
                else:
                    raise

        return super().delete(*args, **kwargs)


# FTL Folders
class FTLFolder(MPTTModel):
    org = models.ForeignKey("FTLOrg", on_delete=models.CASCADE)
    name = CICharField(max_length=128)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete documents in this folder
        documents = FTLDocument.objects.filter(ftl_folder=self, deleted=False)
        for document in documents:
            document.mark_delete()

        # Delete descendants folders recursively
        descendants = self.get_descendants()[::-1]  # slice syntax for reversing
        for descendant in descendants:
            descendant.delete()

        return super().delete(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "parent_id", "org_id"],
                name="folder_name_unique_for_org_level",
            ),
            UniqueConstraint(
                fields=["name", "org_id"],
                condition=Q(parent_id__isnull=True),
                name="folder_name_unique_for_org_level_at_root",
            ),
        ]


# FTL Document sharing
class FTLDocumentSharing(models.Model):
    pid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    ftl_doc = ForeignKey(
        "FTLDocument",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="share_pids",
    )
    created = models.DateTimeField(default=timezone.now)
    edited = models.DateTimeField(auto_now=True)
    expire_at = models.DateTimeField(null=True, blank=True)
    password = models.CharField(null=True, blank=True, max_length=128)
    note = models.TextField(blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return str(self.pid)

    class Meta:
        ordering = ["-created"]


class FTLModelPermissions(DjangoModelPermissions):
    """
    Slightly customized DjangoModelPermissions for FTL. The permissions are very basic and used at instance level.
    It checks for adding or listing document, not to check ownership of a single document.
    """

    # DjangoModelPermissions permissions only cover POST, PUT, DELETE. We set a permission check for GET.
    perms_map = {}
    perms_map.update(DjangoModelPermissions.perms_map)
    perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


def permissions_names_to_objects(names):
    """
    Given an iterable of permissions names (e.g. 'app_label.add_model'),
    return an iterable of Permission objects for them.  The permission
    must already exist, because a permission name is not enough information
    to create a new permission.
    """
    result = []
    for name in names:
        app_label, codename = name.split(".", 1)
        # Is that enough to be unique? Hope so
        result.append(
            Permission.objects.get(content_type__app_label=app_label, codename=codename)
        )

    return result
