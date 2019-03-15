from django.contrib.auth.models import User

from core.models import FTLOrg, FTLUser
from ftests.tools import test_values as tv


def setup_admin(email=tv.ADMIN_EMAIL, username=tv.ADMIN_USERNAME, password=tv.ADMIN_PASS):
    return User.objects.create_superuser(
        email=email,
        username=username,
        password=password,
    )


def setup_org(name=tv.ORG_NAME, slug=tv.ORG_SLUG):
    return FTLOrg.objects.create(
        name=name,
        slug=slug,
    )


def setup_user(org_model, email=tv.USER1_EMAIL, username=tv.USER1_USERNAME, password=tv.USER1_PASS):
    user = User.objects.create_user(
        email=email,
        username=username,
        password=password,
    )
    return FTLUser.objects.create(
        user=user,
        org=org_model,
    )
