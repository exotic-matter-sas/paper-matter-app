from django.contrib.auth.models import User, Group
from rest_framework import serializers

from core.models import FTLDocument, FTLUser, FTLOrg


class FTLOrgSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FTLOrg
        fields = ('url', 'name', 'slug', 'created')


class FTLUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FTLUser
        fields = ('url', 'created', 'org', 'user')


class FTLDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FTLDocument
        fields = ('url', 'title', 'note', 'created', 'edited', 'ftl_user', 'ftl_folder', 'org')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
