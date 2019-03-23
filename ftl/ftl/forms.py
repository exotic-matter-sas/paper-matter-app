from django.contrib.auth.forms import UserCreationForm

from core.models import FTLUser


class FTLUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = UserCreationForm.Meta.fields + ("email",)
