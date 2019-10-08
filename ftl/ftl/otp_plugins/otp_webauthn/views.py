import cbor2
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DeleteView
from fido2.client import ClientData
from fido2.ctap2 import AttestationObject, AttestedCredentialData
from fido2.server import RelyingParty, Fido2Server

from ftl.otp_plugins.otp_webauthn.models import Fido2Device, Fido2State

FIDO2_REGISTER_STATE = 'fido2_register_state'
FIDO2_LOGIN_STATE = 'fido2_login_state'

rp = RelyingParty(settings.FIDO2_RP_ID, "FTL")
fido2 = Fido2Server(rp)


class Fido2Register(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'otp_webauthn/register.html')


class Fido2DeviceList(ListView):
    model = Fido2Device


class Fido2DeviceDelete(DeleteView):
    model = Fido2Device
    success_url = reverse_lazy("otp_webauthn_list")


@csrf_exempt
def fido2_api_register_begin(request):
    registration_data, state = fido2.register_begin({
        "id": b'request.user.id',
        "name": request.user.email,
        "displayName": request.user.email,
        "icon": ""
    })

    request.session[FIDO2_REGISTER_STATE] = state

    return HttpResponse(cbor2.dumps(registration_data), content_type='application/octet-stream')


@csrf_exempt
def fido2_api_register_finish(request):
    data = cbor2.loads(request.body)
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])

    auth_data = fido2.register_complete(request.session[FIDO2_REGISTER_STATE], client_data, att_obj)

    device = Fido2Device(authenticator_data=cbor2.dumps(auth_data.credential_data))
    device.user = request.user
    device.name = "fido2"
    device.confirmed = True
    device.save()

    return HttpResponse(cbor2.dumps({"status": "OK"}), content_type='application/cbor')


@csrf_exempt
def fido2_api_login_begin(request):
    user = request.user
    credentials_query = Fido2Device.objects.filter(user=user)
    credentials = [AttestedCredentialData(cbor2.loads(c.authenticator_data)) for c in credentials_query]
    auth_data, state = fido2.authenticate_begin(credentials)

    Fido2State(user=user, state=cbor2.dumps(state)).save()
    return HttpResponse(cbor2.dumps(auth_data), content_type='application/cbor')
