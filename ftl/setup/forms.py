from django.contrib.auth.forms import UserCreationForm

from core.models import FTLUser, FTLOrg


class AdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        """Set extra attributes to create an admin user"""
        user = super().save(commit=False)
        user.org = FTLOrg.objects.all().first()  # Just pick the first org because there is only one
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
