from django.shortcuts import render, redirect, get_object_or_404

from .models import FTLOrg
from core.forms import FTLUserCreationForm, SelectOrganizationToLoginForm


def signup(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    if request.method == 'POST':
        form = FTLUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:signup_success', org_slug)
    else:
        form = FTLUserCreationForm()

    return render(request, 'core/signup.html', {'form': form, 'org_name': org.name})


def signup_success(request, org_slug):
    return render(request, 'core/signup_success.html', {'org_slug': org_slug})


def login_hub(request):
    if request.method == 'POST':
        form = SelectOrganizationToLoginForm(request.POST)
        if form.is_valid():
            org = get_object_or_404(FTLOrg, name=form.cleaned_data['organization_name'])
            return redirect('app:login', org.slug)
    else:
        form = SelectOrganizationToLoginForm()

    return render(request, 'core/login_hub.html', {'form': form})


def login(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    return render(request, 'core/login.html', {'org_name': org.name})
