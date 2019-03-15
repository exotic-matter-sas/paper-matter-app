from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from setup.forms import AdminCreationForm
from core.models import FTLOrg


def landing_page_step1(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('setup:landing_page_step2')
    else:
        form = AdminCreationForm()

    context = {
        'form': form,
    }

    return render(request, 'setup/admin_creation_form.html', context)


class LandingPageStep2(CreateView):
    model = FTLOrg
    fields = ('name', 'slug')
    template_name = 'setup/first_organization_creation_form.html'

    def get_success_url(self):
        return reverse('setup:success', args=(self.object.slug,))


def success(request, org_slug):
    get_object_or_404(FTLOrg, slug=org_slug)  # To check if org is valid
    context = {
        'org_slug': org_slug,
    }
    return render(request, 'setup/success.html', context)
