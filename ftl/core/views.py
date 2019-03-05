from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from core.models import FTLOrg


@login_required
def home(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    context = {
        'title': _('Home'),
        'org_name': org.name,
        'username': request.user.get_username(),
    }
    return render(request, 'core/home.html', context)



