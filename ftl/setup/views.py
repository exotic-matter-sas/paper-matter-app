from django.views.generic import CreateView
from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect


class LandingPageView(CreateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email', 'password')
    template_name = 'setup/admin_and_first_organization_creation_form.html'

    def form_valid(self, form):
        """Force User fields values to create an admin user"""
        self.object = form.save(commit=False)
        self.object.is_staff = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        """Update form html fields types"""
        form = super(LandingPageView, self).get_form(form_class)
        form.fields['email'].required = True
        form.fields['password'].widget = forms.PasswordInput()
        return form

    def get_success_url(self):
        return reverse('setup:success')


def success(request):
    return render(request, 'setup/setup_success.html')
