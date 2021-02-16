#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

import os
import tempfile
from binascii import a2b_hex

from django.utils import timezone
import cbor2
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from fido2.ctap2 import AttestedCredentialData

from core.models import (
    FTLOrg,
    FTLUser,
    FTLDocument,
    FTLFolder,
    FTLDocumentSharing,
    FTLDocumentReminder,
)
from core.processing.proc_pgsql_tsvector import FTLSearchEnginePgSQLTSVector
from ftests.tools import test_values as tv
from ftl.otp_plugins.otp_ftl.models import Fido2Device
from ftl.settings import BASE_DIR


def setup_org(name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1):
    return FTLOrg.objects.create(name=name, slug=slug,)


def setup_admin(
    org, email=tv.ADMIN1_EMAIL, password=tv.ADMIN1_PASS, lang="en", tz="Europe/Paris"
):
    return FTLUser.objects.create_superuser(
        org=org, email=email, password=password, lang=lang, tz=tz
    )


def setup_user(
    org, email=tv.USER1_EMAIL, password=tv.USER1_PASS, lang="en", tz="Europe/Paris"
):
    user = FTLUser.objects.create_user(
        org=org, email=email, password=password, lang=lang, tz=tz
    )
    # Not used for now
    # user.groups.add(Group.objects.get(name="ftl_users_group"))
    return user


def setup_authenticated_session(test_client, org, user):
    session = test_client.session
    session.update(
        {"org_name": org.name, "org_id": org.id,}
    )
    session.save()
    test_client.force_login(user)


def setup_document(
    org,
    ftl_user,
    ftl_folder=None,
    title=tv.DOCUMENT1_TITLE,
    note=tv.DOCUMENT1_NOTE,
    binary=tv.DOCUMENT1_BINARY_PATH,
    text_content=tv.DOCUMENT1_CONTENT,
    language=tv.DOCUMENT1_LANGUAGE,
    file_type="application/pdf",
    creation_date=None,
):
    document = FTLDocument.objects.create(
        org=org,
        ftl_user=ftl_user,
        ftl_folder=ftl_folder,
        title=title,
        note=note,
        binary=binary,
        content_text=text_content,
        language=language,
        type=file_type,
        created=creation_date if creation_date else timezone.now(),
    )
    # Update document to allow PGSQL to process search vector
    vector_plugin = FTLSearchEnginePgSQLTSVector()
    vector_plugin.process(document, False)

    return document


def setup_folder(org, name=tv.FOLDER1_NAME, parent=None):
    return FTLFolder.objects.create(org=org, name=name, parent=parent,)


def setup_temporary_file():
    f = tempfile.NamedTemporaryFile(
        dir=os.path.join(BASE_DIR, "ftests", "tools"), delete=False
    )
    f.write(b"Hello world!")  # Actual content doesn't matter
    f.close()
    return f


def setup_2fa_static_device(
    ftl_user, name=tv.STATIC_DEVICE_NAME, codes_list=None, confirmed=True
):
    static_device = StaticDevice.objects.create(
        user=ftl_user, name=name, confirmed=confirmed
    )

    if codes_list:
        for code in codes_list:
            StaticToken.objects.create(token=code, device=static_device)

    return static_device


def setup_2fa_totp_device(
    ftl_user, name=tv.TOTP_DEVICE_NAME, secret_key=None, confirmed=True
):

    kwargs = {"user": ftl_user, "name": name, "confirmed": confirmed}

    if secret_key:
        kwargs["key"] = secret_key

    return TOTPDevice.objects.create(**kwargs)


def setup_2fa_fido2_device(ftl_user, name=tv.FIDO2_DEVICE_NAME, confirmed=True):
    # This is a test credential from `fido2` unit test.
    # https://github.com/Yubico/python-fido2/blob/master/test/test_ctap2.py
    fido2_fake_authenticator_data = AttestedCredentialData(
        a2b_hex(
            "f8a011f38c0a4d15800617111f9edc7d0040fe3aac036d14c1e1c65518b698dd1da8f596bc33e11072813466c6bf3845691509b80fb76d59309b8d39e0a93452688f6ca3a39a76f3fc52744fb73948b15783a5010203262001215820643566c206dd00227005fa5de69320616ca268043a38f08bde2e9dc45a5cafaf225820171353b2932434703726aae579fa6542432861fe591e481ea22d63997e1a5290"
        )
    )
    return Fido2Device.objects.create(
        user=ftl_user,
        name=name,
        confirmed=confirmed,
        authenticator_data=cbor2.dumps(fido2_fake_authenticator_data),
    )


def setup_document_share(
    ftl_doc, expire_at=None, password=None, note=tv.DOCUMENT_SHARING_LINK_1_NOTE
):
    return FTLDocumentSharing.objects.create(
        ftl_doc=ftl_doc, expire_at=expire_at, password=password, note=note
    )


def setup_document_reminder(
    ftl_doc, ftl_user, alert_on, note=tv.DOCUMENT_REMINDER_1_NOTE
):
    return FTLDocumentReminder.objects.create(
        ftl_doc=ftl_doc, ftl_user=ftl_user, alert_on=alert_on, note=note
    )
