from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from django.shortcuts import render


@login_required
def home(request):
    context = {
        'title': _('Home'),
        'org_name': request.session['org_name'],
        'username': request.user.get_username(),
    }
    return render(request, 'core/home.html', context)
