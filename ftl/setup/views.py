from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from core.models import FTLOrg, permission_names_to_objects
from setup.forms import AdminCreationForm


class CreateOrg(CreateView):
    model = FTLOrg
    fields = ('name', 'slug')
    template_name = 'setup/first_organization_creation_form.html'
    success_url = reverse_lazy('setup:create_admin')

    def get(self, request, *args, **kwargs):
        if 'ftl_setup_middleware' in request.session:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login')


class CreateAdmin(FormView):
    template_name = 'setup/admin_creation_form.html'
    form_class = AdminCreationForm  # Custom form for enabling admin flag
    success_url = reverse_lazy('setup:success')

    def get(self, request, *args, **kwargs):
        if 'ftl_setup_middleware' in request.session:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login')

    def form_valid(self, form):
        instance = form.save(commit=False)  # save admin user

        instance.org = FTLOrg.objects.all().first()  # Just pick the first org because there is only one
        instance.is_superuser = True
        instance.is_staff = True
        # Need to actual save in DB to get the ID and then we can set the permissions many-2-many relation
        instance.save()
        instance.user_permissions.set(permission_names_to_objects([
            'core.add_ftluser',
            'core.change_ftluser',
            'core.delete_ftluser',
            'core.view_ftluser',
            'core.add_ftldocument',
            'core.change_ftldocument',
            'core.delete_ftldocument',
            'core.view_ftldocument',
            'core.add_ftlfolder',
            'core.change_ftlfolder',
            'core.delete_ftlfolder',
            'core.view_ftlfolder',
            'core.add_ftlorg',
            'core.change_ftlorg',
            'core.delete_ftlorg',
            'core.view_ftlorg',
        ]))
        instance.save()

        return super().form_valid(form)


def success(request):
    org = get_object_or_404(FTLOrg)
    context = {
        'org_slug': org.slug,
        'org_name': org.name,
    }
    return render(request, 'setup/success.html', context)
