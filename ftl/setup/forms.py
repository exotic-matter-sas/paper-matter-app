from django.contrib.auth.forms import UserCreationForm

from core.models import FTLUser


class AdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = UserCreationForm.Meta.fields + ("email",)
