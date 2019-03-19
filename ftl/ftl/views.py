from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from core.models import FTLOrg, FTLUser
from ftl.forms import FTLUserCreationForm


def index(request):
    admin_users = FTLUser.objects.filter(is_staff=True).count()
    if admin_users > 0:
        return redirect('login')
    else:
        if FTLOrg.objects.count() > 0:
            return redirect('setup:create_admin')
        else:
            return redirect('setup:create_org')


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
        form.save_user(self.kwargs['org_slug'])
        return super().form_valid(form)


def signup_success(request, org_slug):
    context = {
        'org_slug': org_slug,
    }

    return render(request, 'ftl/signup_success.html', context)
