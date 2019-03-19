from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from core.models import FTLOrg
from setup.forms import AdminCreationForm


class CreateOrg(CreateView):
    model = FTLOrg
    fields = ('name', 'slug')
    template_name = 'setup/first_organization_creation_form.html'
    success_url = reverse_lazy('setup:create_admin')


class CreateAdmin(FormView):
    template_name = 'setup/admin_creation_form.html'
    form_class = AdminCreationForm  # Custom form for enabling admin flag
    success_url = reverse_lazy('setup:success')

    def form_valid(self, form):
        form.save()  # save admin user
        return super().form_valid(form)


def success(request):
    org = get_object_or_404(FTLOrg)
    context = {
        'org_slug': org.slug,
        'org_name': org.name,
    }
    return render(request, 'setup/success.html', context)
