from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView

from core.models import FTLOrg
from setup.forms import AdminCreationFrom


def landing_page_step1(request):
    if request.method == 'POST':
        form = AdminCreationFrom(request.POST)
        if form.is_valid():
            form.save()
            return redirect('setup:landing_page_step2')
    else:
        form = AdminCreationFrom()

    return render(request, 'setup/admin_creation_form.html', {'form': form})


class LandingPageStep2(CreateView):
    model = FTLOrg
    fields = ('name', 'slug')
    template_name = 'setup/first_organization_creation_form.html'

    def get_success_url(self):
        return reverse('setup:success', args=(self.object.slug,))


def success(request, org_slug):
    return render(request, 'setup/success.html', {'org_slug': org_slug})
