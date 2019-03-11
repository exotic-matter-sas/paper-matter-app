from django.contrib.auth.models import User

from core.models import FTLOrg
from ftests.tools import test_values as tv


def setup_admin(email=tv.ADMIN_EMAIL, username=tv.ADMIN_USERNAME):
    # TODO find a programatic way of properly create admin
    User.objects.create(
        email=email,
        username=username,
        is_superuser=True,
        is_staff=True,
    )


def setup_org(name=tv.ORG_NAME, slug=tv.ORG_SLUG):
    FTLOrg.objects.create(
        name=name,
        slug=slug,
    )
