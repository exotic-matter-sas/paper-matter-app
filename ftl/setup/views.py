from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from core.models import FTLOrg, FTL_PERMISSIONS_USER, permissions_names_to_objects
from setup.forms import FirstOrgAndAdminCreationForm


class CreateFirstOrgAndAdmin(FormView):
    template_name = 'setup/first_org_and_admin_creation_form.html'
    form_class = FirstOrgAndAdminCreationForm  # Custom form for enabling admin flag
    success_url = reverse_lazy('setup:success')

    def get(self, request, *args, **kwargs):
        if 'ftl_setup_middleware' in request.session:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login')

    def form_valid(self, form):
        instance = form.save(commit=True)
        instance.user_permissions.set(permissions_names_to_objects(FTL_PERMISSIONS_USER))
        instance.save()

        return super().form_valid(form)


def success(request):
    org = get_object_or_404(FTLOrg)
    context = {
        'org_slug': org.slug,
        'org_name': org.name,
    }
    return render(request, 'setup/success.html', context)
