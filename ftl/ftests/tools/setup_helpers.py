#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

import os
import tempfile

from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from core.models import (
    FTLOrg,
    FTLUser,
    FTLDocument,
    FTLFolder,
    FTLDocumentSharing,
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
    type="application/pdf",
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
        type=type,
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
    return Fido2Device.objects.create(user=ftl_user, name=name, confirmed=confirmed)


def setup_document_share(
    ftl_doc, expire_at=None, password=None, note=tv.DOCUMENT_SHARING_LINK_1_NOTE
):
    return FTLDocumentSharing.objects.create(
        ftl_doc=ftl_doc, expire_at=expire_at, password=password, note=note
    )
