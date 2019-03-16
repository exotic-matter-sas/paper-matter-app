from django.contrib.auth.forms import UserCreationForm

from core.models import FTLUser, FTLOrg


class FTLUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = UserCreationForm.Meta.fields + ("email",)

    def save_user(self, slug):
        # Need a second method for saving because we need the slug in parameter (given by the view on form submit)
        # We can't access captured url argument in here.
        user = super().save(commit=False)
        user.org = FTLOrg.objects.get(slug=slug)
        user.save()
        return user

    def save(self, commit=True):
        # Disable the standard save() method
        raise NotImplementedError
