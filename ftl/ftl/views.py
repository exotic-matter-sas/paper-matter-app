from django.shortcuts import render, redirect, get_object_or_404

from core.forms import FTLUserCreationForm, SelectOrganizationToLoginForm
from core.models import FTLOrg, FTLUser


def index(request):
    admin_users = FTLUser.objects.filter(is_staff=True).count()
    if admin_users:
        if FTLOrg.objects.count():
            return redirect('login')
        else:
            return redirect('setup:landing_page_step2')
    else:
        return redirect('setup:landing_page_step1')


def signup(request, org_slug):
    org = get_object_or_404(FTLOrg, slug=org_slug)
    if request.method == 'POST':
        form = FTLUserCreationForm(request.POST)
        if form.is_valid():
            save = form.save()
            ftl_user = FTLUser(user=save, org=org)
            ftl_user.save()

            return redirect('signup_success', org_slug)
    else:
        form = FTLUserCreationForm()

    context = {
        'form': form,
        'org_name': org.name,
    }

    return render(request, 'ftl/signup.html', context)


def signup_success(request, org_slug):
    context = {
        'org_slug': org_slug,
    }

    return render(request, 'ftl/signup_success.html', context)


def login_hub(request):
    if request.method == 'POST':
        form = SelectOrganizationToLoginForm(request.POST)
        if form.is_valid():
            org = get_object_or_404(FTLOrg, slug=form.cleaned_data['organization_slug'])
            return redirect('login', org.slug)
    else:
        form = SelectOrganizationToLoginForm()

    context = {
        'form': form,
    }

    return render(request, 'ftl/login_hub.html', context)
