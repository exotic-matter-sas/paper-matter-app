from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from core.models import FTLOrg
from core.forms import FTLUserCreationForm, SelectOrganizationToLoginForm


def index(request):
    admin_users = User.objects.filter(is_staff=True).count()
    if admin_users:
        if FTLOrg.objects.count():
            return redirect('login_hub')
        else:
            return redirect('setup:landing_page_step2')
    else:
        return redirect('setup:landing_page_step1')


def signup(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    if request.method == 'POST':
        form = FTLUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup_success', org_slug)
    else:
        form = FTLUserCreationForm()

    return render(request, 'ftl/signup.html', {'form': form, 'org_name': org.name})


def signup_success(request, org_slug):
    return render(request, 'ftl/signup_success.html', {'org_slug': org_slug})


def login_hub(request):
    if request.method == 'POST':
        form = SelectOrganizationToLoginForm(request.POST)
        if form.is_valid():
            org = get_object_or_404(FTLOrg, slug=form.cleaned_data['organization_slug'])
            return redirect('login', org.slug)
    else:
        form = SelectOrganizationToLoginForm()

    return render(request, 'ftl/login_hub.html', {'form': form})
