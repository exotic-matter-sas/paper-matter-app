from django.shortcuts import redirect
from django.contrib.auth.models import User
from core.models import FTLOrg


def index(request):
    admin_users = User.objects.filter(is_staff=True).count()
    if admin_users:
        if FTLOrg.objects.count():
            return redirect('app:login')
        else:
            return redirect('setup:landing_page_step2')
        else:
            return redirect('app:login_hub')

