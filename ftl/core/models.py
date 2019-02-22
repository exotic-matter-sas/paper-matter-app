from django.contrib.auth.models import User
from django.db import models


# FTP orgs
class FTLOrg(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)  # URL of the org
    created = models.DateTimeField(auto_now_add=True)


# FTL user (linked to Django user)
class FTLUser(models.Model):
    ftl_user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django user system
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


# FTL Documents
class FTLDocument(models.Model):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    ftl_user = models.ForeignKey('FTLUser', on_delete=models.CASCADE)
    title = models.TextField()
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
