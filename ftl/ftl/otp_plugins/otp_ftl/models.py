import base64

import cbor2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django_otp.models import Device
from fido2.client import ClientData
from fido2.ctap2 import AuthenticatorData, AttestedCredentialData
from fido2.server import RelyingParty, Fido2Server

rp = RelyingParty(settings.FIDO2_RP_ID, settings.FIDO2_RP_NAME)
fido2 = Fido2Server(rp)


class Fido2State(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    state = models.BinaryField()
    created = models.DateTimeField(auto_now_add=True)


class Fido2Device(Device):
    authenticator_data = models.BinaryField()

    def verify_token(self, token):
        state = Fido2State.objects.filter(user=self.user).last()
        state.delete()
        state_decode = cbor2.loads(state.state)

        data = cbor2.loads(base64.b64decode(token))
        credential_id = data["credentialId"]
        client_data = ClientData(data["clientDataJSON"])
        auth_data = AuthenticatorData(data["authenticatorData"])
        signature = data["signature"]

        credentials_query = Fido2Device.objects.filter(user=self.user)
        credentials = [AttestedCredentialData(cbor2.loads(c.authenticator_data)) for c in credentials_query]

        fido2.authenticate_complete(
            state_decode,
            credentials,
            credential_id,
            client_data,
            auth_data,
            signature,
        )

        return True
