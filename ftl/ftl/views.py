#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django_registration.backends.activation.views import RegistrationView

from core.models import FTLOrg
from ftl.forms import FTLUserCreationForm, FTLCreateOrgAndFTLUser


class CreateFTLUserFormView(RegistrationView):
    template_name = "ftl/registration/signup.html"
    form_class = FTLUserCreationForm
    success_url = reverse_lazy("signup_success")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        org = get_object_or_404(FTLOrg.objects.filter(slug=self.kwargs["org_slug"]))
        data["org_name"] = org.name
        return data

    def form_valid(self, form):
        org = get_object_or_404(FTLOrg, slug=self.kwargs["org_slug"])
        instance = form.save(commit=False)
        instance.org = org
        instance.save()

        ftl_group = Group.objects.get(name="ftl_users_group")
        instance.groups.add(ftl_group)

        instance.save()

        return super().form_valid(form)


def signup_success(request):
    return render(request, "ftl/registration/signup_success.html")


class SetMessageAndRedirectView(RedirectView):
    """
    View for showing a flash message
    """

    message_type = messages.SUCCESS
    message = None

    def get(self, request, *args, **kwargs):
        messages.add_message(request, self.message_type, self.message)
        return super().get(request, *args, **kwargs)


class PasswordResetAsked(SetMessageAndRedirectView):
    url = reverse_lazy("login")
    message = _(
        "We’ve emailed you instructions for setting your password, if an account exists with the email "
        "you entered. You should receive them shortly (check your spam folder if that's not the case)."
    )


class PasswordResetDone(SetMessageAndRedirectView):
    url = reverse_lazy("login")
    message = _("Your password has been set. You may go ahead and log in now.")


class CreateOrgAndFTLUser(RegistrationView):
    template_name = "ftl/registration/create_org_and_ftluser.html"
    form_class = FTLCreateOrgAndFTLUser
    success_url = reverse_lazy("signup_success")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs[
            "lang"
        ] = self.request.LANGUAGE_CODE  # Use Django detected language for the account
        return kwargs


class AccountActivationSuccess(SetMessageAndRedirectView):
    url = reverse_lazy("login")
    message = _(
        "Your email has been verified, thank you! You may go ahead and log in now."
    )
