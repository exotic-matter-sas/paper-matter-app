import os
import pathlib
import uuid

from django.contrib.auth.models import User, AbstractUser, Permission
from django.contrib.postgres.fields.citext import CICharField
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from rest_framework.permissions import DjangoModelPermissions

FTL_PERMISSIONS_USER = [
    'core.add_ftldocument',
    'core.change_ftldocument',
    'core.delete_ftldocument',
    'core.view_ftldocument',
    'core.add_ftlfolder',
    'core.change_ftlfolder',
    'core.delete_ftlfolder',
    'core.view_ftlfolder',
]


def _get_name_binary(instance, filename):
    return 'uploads/' + str(uuid.uuid4()) + pathlib.Path(filename).suffix


# FTP orgs
class FTLOrg(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)  # URL of the org
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# FTL users
class FTLUser(AbstractUser):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    # override email field to set blank and unique constrains
    email = models.EmailField(_('email address'), blank=False, unique=True)

    def __str__(self):
        return self.username


# FTL Documents
class FTLDocument(models.Model):
    pid = models.UUIDField(default=uuid.uuid4, editable=False)

    org = models.ForeignKey('FTLOrg', on_delete=models.PROTECT)
    ftl_user = models.ForeignKey('FTLUser', on_delete=models.PROTECT)
    ftl_folder = TreeForeignKey('FTLFolder', on_delete=models.PROTECT, null=True, blank=True)
    title = models.TextField()
    note = models.TextField(blank=True)
    content_text = models.TextField(blank=True)
    binary = models.FileField(upload_to=_get_name_binary, max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    tsvector = SearchVectorField(blank=True)
    language = models.CharField(max_length=64, default="english")
    thumbnail_binary = models.FileField(upload_to=_get_name_binary, max_length=256, null=True)

    # // TODO tsvector index missing
    # class Meta:
    #     indexes = [
    #         GinIndex(fields=['tsvector'])
    #     ]

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Override to ensure document file is deleted"""

        binary = self.binary
        thumbnail_binary = self.thumbnail_binary

        if binary:
            binary.file.close()
            os.remove(binary.file.name)

        if thumbnail_binary:
            thumbnail_binary.file.close()
            os.remove(thumbnail_binary.file.name)

        super().delete(*args, **kwargs)


# FTL Folders
class FTLFolder(MPTTModel):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    name = CICharField(max_length=128)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete documents in this folder
        documents = FTLDocument.objects.filter(ftl_folder=self)
        for document in documents:
            document.delete()

        # Delete descendants folders recursively
        descendants = self.get_descendants()[::-1]  # slice syntax for reversing
        for descendant in descendants:
            descendant.delete()

        super().delete(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'level', 'org_id'], name='folder_name_unique_for_org_level'),
        ]


class FTLModelPermissions(DjangoModelPermissions):
    """
    Slightly customized DjangoModelPermissions for FTL. The permissions are very basic and used at instance level.
    It checks for adding or listing document, not to check ownership of a single document.
    """
    # DjangoModelPermissions permissions only cover POST, PUT, DELETE. We set a permission check for GET.
    perms_map = {}
    perms_map.update(DjangoModelPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


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
        result.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))

    return result
