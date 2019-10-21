from django import forms
from django_otp.forms import OTPTokenForm


class OTPTokenFormFido2(OTPTokenForm):
    otp_device = forms.ChoiceField(choices=[])
    otp_token = forms.CharField(required=True, widget=forms.HiddenInput())
    otp_challenge = None

    def __init__(self, user, request=None, *args, **kwargs):
        super(OTPTokenForm, self).__init__(*args, **kwargs)

        self.user = user
        self.fields['otp_device'].choices = [d for d in self.device_choices(user) if 'otp_webauthn' in d[0]]
