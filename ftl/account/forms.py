from django import forms
from django.contrib.auth import get_user_model


class EmailUpdateForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput)

    class Meta:
        model = get_user_model()
        fields = ['email']
