from core.models import FTLOrg
from ftests.tools import test_values as tv


def setup_org(name=tv.ORG_NAME, slug=tv.ORG_SLUG):
    FTLOrg.objects.create(
        name=name,
        slug=slug,
    )


