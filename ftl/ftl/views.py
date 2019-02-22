from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    try:
        u = User.objects.get(username='admin')
    except ObjectDoesNotExist:
        return redirect('setup:index')
    else:
        pass
        # TODO redirect to user login page
