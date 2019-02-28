from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    try:
        u = User.objects.get(is_staff=True)
    except ObjectDoesNotExist:
        return redirect('setup:landing_page')
    else:
        return redirect('app:login')

