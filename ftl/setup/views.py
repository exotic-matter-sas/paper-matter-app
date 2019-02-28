from django.views.generic import CreateView
from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from core.models import FTLOrg


class LandingPageStep1View(CreateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email', 'password')
    template_name = 'setup/admin_creation_form.html'

    def form_valid(self, form):
        """Set is_staff value to create an admin user"""
        self.object = form.save(commit=False)
        self.object.is_staff = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        """Update form html fields types"""
        form = super(LandingPageStep1View, self).get_form(form_class)
        form.fields['email'].required = True
        form.fields['password'].widget = forms.PasswordInput()
        return form

    def get_success_url(self):
        return reverse('setup:landing_page_step2')


class LandingPageStep2View(CreateView):
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
        return reverse('setup:success')


def success(request):
    return render(request, 'setup/success.html')
