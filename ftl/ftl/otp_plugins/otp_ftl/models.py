#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import base64
import logging

import cbor2
from django.conf import settings
from django.db import models
from django_otp.models import Device
from fido2.client import ClientData
from fido2.ctap2 import AuthenticatorData, AttestedCredentialData
from fido2.server import PublicKeyCredentialRpEntity, Fido2Server

logger = logging.getLogger(__name__)


class Fido2Device(Device):
    authenticator_data = models.BinaryField()

    def verify_token(self, token):
        data = cbor2.loads(base64.b64decode(token["token"]))
        credential_id = data["credentialId"]
        client_data = ClientData(data["clientDataJSON"])
        auth_data = AuthenticatorData(data["authenticatorData"])
        signature = data["signature"]
        state = token["state"]
        domain = token["domain"]

        credentials_query = Fido2Device.objects.filter(user=self.user)
        credentials = [
            AttestedCredentialData(cbor2.loads(c.authenticator_data))
            for c in credentials_query
        ]

        rp = PublicKeyCredentialRpEntity(domain, settings.FIDO2_RP_NAME)
        fido2 = Fido2Server(rp)

        try:
            fido2.authenticate_complete(
                state, credentials, credential_id, client_data, auth_data, signature,
            )

            return True
        except ValueError:
            logger.exception("Error in FIDO2 final authentication")
            return False
