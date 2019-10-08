import json

from django import forms
from django.conf import settings
from django.contrib import admin
from fido2.server import RelyingParty, Fido2Server

from ftl.otp_plugins.otp_webauthn.models import Fido2Device


class FIDO2DeviceAdminForm(forms.ModelForm):
    user = forms.CharField()
    challenge = forms.CharField()
    device_response = forms.CharField()

    def __init__(self, *args, **kwargs):
        rp = RelyingParty(settings.FIDO2_RP_ID, "FTL")
        fido2 = Fido2Server(rp)

        registration_data, state = fido2.register_begin({
            "id": bytes(kwargs['user'].id),
            "name": kwargs['user'].email,
        })

        initial = kwargs.get('initial', {})
        initial['challenge'] = json.dumps(registration_data)
        kwargs['initial'] = initial
        super(FIDO2DeviceAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Fido2Device
        fields = ['challenge', 'device_response']


class FIDO2DeviceModelAdmin(admin.ModelAdmin):
    form = FIDO2DeviceAdminForm



admin.site.register(Fido2Device)
