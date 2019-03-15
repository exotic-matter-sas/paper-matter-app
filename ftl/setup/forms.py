from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User

from core.models import FTLUser


class AdminCreationForm(UserCreationForm):

    class Meta:
        model = FTLUser
        fields = ("email", "username",)
        field_classes = {'username': UsernameField}

    def save(self, commit=True):
        """Set extra attributes to create an admin user"""
        user = super().save(commit=False)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
