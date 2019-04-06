import pathlib
import uuid

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


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

    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    ftl_user = models.ForeignKey('FTLUser', on_delete=models.CASCADE)
    ftl_folder = TreeForeignKey('FTLFolder', on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField()
    note = models.TextField(blank=True)
    binary = models.FileField(upload_to=_get_name_binary, max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# FTL Folders
class FTLFolder(MPTTModel):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
