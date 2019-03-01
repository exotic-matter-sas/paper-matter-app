from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User


class AdminCreationFrom(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username",)
        field_classes = {'username': UsernameField}

    def save(self):
        """Set extra attributes to create an admin user"""
        user = super().save(commit=False)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
