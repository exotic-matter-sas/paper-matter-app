#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import cbor2
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, UpdateView
from django_otp.decorators import otp_required
from fido2.client import ClientData
from fido2.ctap2 import AttestationObject, AttestedCredentialData
from fido2.server import PublicKeyCredentialRpEntity, Fido2Server

from ftl.otp_plugins.otp_ftl.forms import Fido2DeviceCheckForm
from ftl.otp_plugins.otp_ftl.models import Fido2Device
from ftl.otp_plugins.otp_ftl.views import FTLBaseCheckView, FTLBaseDeleteView

FIDO2_REGISTER_STATE = "fido2_register_state"
FIDO2_LOGIN_STATE = "fido2_login_state"


@method_decorator(login_required, name="dispatch")
class Fido2Check(FTLBaseCheckView):
    template_name = "otp_ftl/fido2device_check.html"
    form_class = Fido2DeviceCheckForm
    success_url = reverse_lazy("home")


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class Fido2DeviceSuccess(TemplateView):
    template_name = "otp_ftl/fido2device_detail.html"


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class Fido2DeviceUpdate(UpdateView):
    model = Fido2Device
    fields = ["name"]
    template_name = "otp_ftl/device_update.html"
    success_url = reverse_lazy("otp_list")


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class Fido2DeviceAdd(View):
    def get(self, request, *args, **kwargs):
        return render(request, "otp_ftl/fido2device_form.html")


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class Fido2DeviceDelete(FTLBaseDeleteView):
    template_name = "otp_ftl/device_confirm_delete.html"
    model = Fido2Device
    success_url = reverse_lazy("otp_list")


@csrf_exempt
@login_required
@otp_required(if_configured=True)
def fido2_api_register_begin(request):
    rp = PublicKeyCredentialRpEntity(get_domain(request), settings.FIDO2_RP_NAME)
    fido2 = Fido2Server(rp)

    all_devices = Fido2Device.objects.filter(user=request.user)

    registration_data, state = fido2.register_begin(
        {
            "id": request.user.email.encode(),
            "name": request.user.email,
            "displayName": request.user.email,
            "icon": "",
        },
        # Pass existing fido2 credentials to prevent duplicate
        credentials=[
            AttestedCredentialData(cbor2.loads(d.authenticator_data))
            for d in all_devices
        ],
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    request.session[FIDO2_REGISTER_STATE] = state

    return HttpResponse(
        cbor2.dumps(registration_data), content_type="application/octet-stream"
    )


@csrf_exempt
@login_required
@otp_required(if_configured=True)
def fido2_api_register_finish(request):
    data = cbor2.loads(request.body)
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])

    rp = PublicKeyCredentialRpEntity(get_domain(request), settings.FIDO2_RP_NAME)
    fido2 = Fido2Server(rp)
    auth_data = fido2.register_complete(
        request.session[FIDO2_REGISTER_STATE], client_data, att_obj
    )

    device = Fido2Device(authenticator_data=cbor2.dumps(auth_data.credential_data))
    device.user = request.user
    device.name = data["name"] or "Fido key"
    device.confirmed = True
    device.save()

    return HttpResponse(cbor2.dumps({"status": "OK"}), content_type="application/cbor")


@csrf_exempt
@login_required
def fido2_api_login_begin(request):
    user = request.user
    credentials_query = Fido2Device.objects.filter(user=user)
    credentials = [
        AttestedCredentialData(cbor2.loads(c.authenticator_data))
        for c in credentials_query
    ]

    rp = PublicKeyCredentialRpEntity(get_domain(request), settings.FIDO2_RP_NAME)
    fido2 = Fido2Server(rp)
    auth_data, state = fido2.authenticate_begin(
        credentials, user_verification="discouraged"
    )

    request.session["fido2_state"] = state
    request.session["fido2_domain"] = get_domain(request)
    return HttpResponse(cbor2.dumps(auth_data), content_type="application/cbor")


def get_domain(request):
    return request.get_host().split(":", 1)[0]
