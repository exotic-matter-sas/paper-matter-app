from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
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

    context = {
        'title': _('Landing page (1/2)'),
        'form': form,
    }

    return render(request, 'setup/admin_creation_form.html', context)


class LandingPageStep2(CreateView):
    model = FTLOrg
    fields = ('name', 'slug')
    template_name = 'setup/first_organization_creation_form.html'

    def get_context_data(self, **kwargs):
        # Add data to view context
        kwargs['title'] = _('Landing page (2/2)')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('setup:success', args=(self.object.slug,))


def success(request, org_slug):
    context = {
        'title': _('Setup completed'),
        'org_slug': org_slug,
    }
    return render(request, 'setup/success.html', context)
