from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from setup.forms import AdminCreationFrom
from core.models import FTLOrg


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
    fields = ('name',)
    template_name = 'setup/first_organization_creation_form.html'

    def form_valid(self, form):
        """Set slug value"""
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('setup:success', args=(self.object.slug,))


def success(request, org_slug):
    return render(request, 'setup/success.html', {'org_slug': org_slug})
