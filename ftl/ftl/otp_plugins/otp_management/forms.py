from django import forms
from django.forms import Form
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice


class StaticDeviceForm(Form):
    name = forms.CharField(label="Name", initial='ER Code')

    def save(self, user):
        static_device = StaticDevice(name=self.cleaned_data['name'], user=user)
        static_device.save()

        for i in range(10):
            code = StaticToken(token=StaticToken.random_token())
            code.device = static_device
            code.save()


class TOTPDeviceForm(Form):
    name = forms.CharField(label="Name", initial='App authenticator')

    def save(self, user):
        totp_device = TOTPDevice(name=self.cleaned_data['name'], user=user)
        totp_device.save()


class Fido2DeviceForm(Form):
    name = forms.CharField(label="Name", initial='App authenticator')

    def save(self, user):
        totp_device = TOTPDevice(name=self.cleaned_data['name'], user=user)
        totp_device.save()
