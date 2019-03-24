from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings as django_settings

from core.models import FTLOrg, FTLUser
from ftests.tools import test_values as tv


def setup_org(name=tv.ORG_NAME, slug=tv.ORG_SLUG):
    return FTLOrg.objects.create(
        name=name,
        slug=slug,
    )


def setup_admin(org, email=tv.ADMIN_EMAIL, username=tv.ADMIN_USERNAME, password=tv.ADMIN_PASS):
    return FTLUser.objects.create_superuser(
        email=email,
        username=username,
        password=password,
        org=org,
    )


def setup_user(org, email=tv.USER1_EMAIL, username=tv.USER1_USERNAME, password=tv.USER1_PASS):
    return FTLUser.objects.create_user(
        email=email,
        username=username,
        password=password,
        org=org,
    )


def setup_authenticated_session(test_client, org, user):
    session = test_client.session
    session.update({
        'org_name': org.name,
        'org_id': org.id,
    })
    session.save()
    test_client._login(user)
