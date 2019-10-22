from django import forms
from django.forms import Form
from django_otp.forms import OTPTokenForm
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

# Forms for checking
from ftl.otp_plugins.otp_ftl.models import Fido2Device


class StaticDeviceCheckForm(OTPTokenForm):
    otp_challenge = None

    def __init__(self, user, request=None, *args, **kwargs):
        super(OTPTokenForm, self).__init__(*args, **kwargs)

        self.user = user
        self.fields['otp_device'].choices = [d for d in self.device_choices(user) if StaticDevice.model_label() in d[0]]


class TOTPDeviceCheckForm(OTPTokenForm):
    otp_challenge = None

    def __init__(self, user, request=None, *args, **kwargs):
        super(OTPTokenForm, self).__init__(*args, **kwargs)

        self.user = user
        self.fields['otp_device'].choices = [d for d in self.device_choices(user) if TOTPDevice.model_label() in d[0]]


class Fido2DeviceCheckForm(OTPTokenForm):
    otp_device = forms.ChoiceField(choices=[])
    otp_token = forms.CharField(required=True, widget=forms.HiddenInput())
    otp_challenge = None

    def __init__(self, user, request=None, *args, **kwargs):
        super(OTPTokenForm, self).__init__(*args, **kwargs)

        self.user = user
        self.fields['otp_device'].choices = [d for d in self.device_choices(user) if Fido2Device.model_label() in d[0]]


# Forms for registering a new device
class StaticDeviceForm(Form):
    name = forms.CharField(label="Name", initial='ER Code')

    def save(self, user):
        static_device = StaticDevice(name=self.cleaned_data['name'], user=user)
        static_device.save()

        for i in range(10):
            code = StaticToken(token=StaticToken.random_token())
            code.device = static_device
            code.save()

        return static_device


class TOTPDeviceForm(Form):
    name = forms.CharField(label="Name", initial='App authenticator')

    def save(self, user):
        totp_device = TOTPDevice(name=self.cleaned_data['name'], user=user)
        totp_device.confirmed = False
        totp_device.save()

        return totp_device
