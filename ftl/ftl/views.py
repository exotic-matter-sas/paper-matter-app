from django.shortcuts import redirect
from django.contrib.auth.models import User
from core.models import FTLOrg
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    try:
        User.objects.get(is_staff=True)
    except ObjectDoesNotExist:
        return redirect('setup:landing_page_step1')
    else:
        try:
            FTLOrg.objects.get()
        except ObjectDoesNotExist:
            return redirect('setup:landing_page_step2')
        else:
            return redirect('app:login')

