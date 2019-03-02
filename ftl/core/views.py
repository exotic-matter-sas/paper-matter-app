from django.shortcuts import render, redirect, get_object_or_404

from .models import FTLOrg
from core.forms import FTLUserCreationFrom


def signup(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    if request.method == 'POST':
        form = FTLUserCreationFrom(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:signup_success', org_slug)
    else:
        form = FTLUserCreationFrom()

    return render(request, 'core/signup.html', {'form': form, 'org_name': org.name})


def signup_success(request, org_slug):
    return render(request, 'core/signup_success.html', {'org_slug': org_slug})


def login_hub(request):
    return render(request, 'core/login_hub.html')


def login(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    return render(request, 'core/login.html', {'org_name': org.name})
