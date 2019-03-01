from django.shortcuts import redirect
from django.contrib.auth.models import User
from core.models import FTLOrg


def index(request):
    admin_users = User.objects.filter(is_staff=True)
    if not admin_users:
        return redirect('setup:landing_page_step1')
    else:
        organizations = FTLOrg.objects.filter()
        if not organizations:
            return redirect('setup:landing_page_step2')
        else:
            return redirect('app:login')

