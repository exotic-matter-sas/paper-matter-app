from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, RedirectView

from core.models import FTLOrg, permissions_names_to_objects, FTL_PERMISSIONS_USER
from ftl.forms import FTLUserCreationForm


class CreateFTLUserFormView(FormView):
    template_name = 'ftl/signup.html'
    form_class = FTLUserCreationForm

    def get_success_url(self):
        # We redefine the method instead of the field because the success url is dynamic (org slug)
        return reverse('signup_success', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        org = get_object_or_404(FTLOrg.objects.filter(slug=self.kwargs['org_slug']))
        data['org_name'] = org.name
        return data

    def form_valid(self, form):
        org = get_object_or_404(FTLOrg, slug=self.kwargs['org_slug'])
        instance = form.save(commit=False)
        instance.org = org
        instance.save()

        instance.user_permissions.set(permissions_names_to_objects(FTL_PERMISSIONS_USER))

        instance.save()

        return super().form_valid(form)


def signup_success(request, org_slug):
    context = {
        'org_slug': org_slug,
    }

    return render(request, 'ftl/signup_success.html', context)


class SetMessageAndRedirectView(RedirectView):
    message_type = messages.SUCCESS
    message = None

    def get(self, request, *args, **kwargs):
        messages.add_message(request, self.message_type, self.message)
        return super().get(request, *args, **kwargs)
