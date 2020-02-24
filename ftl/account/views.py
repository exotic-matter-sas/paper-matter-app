#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.core.signing import SignatureExpired, BadSignature
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import FormView
from django_otp.decorators import otp_required

from account.forms import EmailSendForm
from core.ftl_mixins import FTLUserContextDataMixin
from core.models import FTLUser


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class AccountView(FTLUserContextDataMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/account_index.html', self.get_context_data())


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class AccountEmailChangeView(SuccessMessageMixin, FTLUserContextDataMixin, FormView):
    template_name = "account/account_email.html"
    email_change_subject = "account/account_email_change_subject.txt"
    email_warn_subject = "account/account_email_warn_subject.txt"
    email_change_body = "account/account_email_change_body.txt"
    email_warn_body = "account/account_email_warn_body.txt"
    form_class = EmailSendForm
    success_url = reverse_lazy('account_index')
    success_message = _("A confirmation email has been sent.")

    def get_email_context(self, activation_key):
        scheme = 'https' if self.request.is_secure() else 'http'
        return {
            'scheme': scheme,
            'activation_key': activation_key,
            'expiration_minutes': 10,
            'site': get_current_site(self.request)
        }

    def form_valid(self, form):
        email_ = form.cleaned_data['email']

        if FTLUser.objects.filter(email=email_).exists():
            form.add_error('email', _("Email is already used by someone else."))
            return super().form_invalid(form)

        # Encode new email and sign it
        activation_key = signing.dumps(
            obj={'id': self.request.user.id, 'old_email': self.request.user.email, 'new_email': email_},
            salt='email_change'
        )

        # Email sent to the new address for validation
        subject_change = render_to_string(
            template_name=self.email_change_subject,
            context=self.get_email_context(activation_key),
            request=self.request
        )
        subject_change = ''.join(subject_change.splitlines())
        message_change = render_to_string(
            template_name=self.email_change_body,
            context=self.get_email_context(activation_key),
            request=self.request
        )

        # Email sent to the current address for notification
        subject_warn = render_to_string(
            template_name=self.email_warn_subject,
            context={},
            request=self.request
        )
        subject_warn = ''.join(subject_warn.splitlines())
        message_warn = render_to_string(
            template_name=self.email_warn_body,
            context={},
            request=self.request
        )

        self.request.user.email_user(subject_warn, message_warn, settings.DEFAULT_FROM_EMAIL)
        send_mail(subject_change, message_change, settings.DEFAULT_FROM_EMAIL, [email_])

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class AccountEmailChangeValidateView(View):
    success_message = _("Email successfully updated.")
    expired_message = _("The link expired. Please try again.")
    incorrect_signature = _("Could not validate your email. Please try again.")

    def get(self, request, *args, **kwargs):
        if 'token' in kwargs:
            # check for validity
            try:
                email_change_request = signing.loads(
                    kwargs['token'],
                    salt='email_change',
                    max_age=timedelta(minutes=10)
                )

                user = self.request.user

                if user.email == email_change_request['old_email'] and user.id == email_change_request['id']:
                    user.email = email_change_request['new_email']
                    user.save()
                    messages.success(self.request, self.success_message)
                else:
                    messages.error(self.request, self.incorrect_signature)
            except SignatureExpired:
                messages.error(self.request, self.expired_message)
            except BadSignature:
                messages.error(self.request, self.incorrect_signature)

        return HttpResponseRedirect(reverse_lazy('account_index'))


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class AccountPasswordView(FTLUserContextDataMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = "account/account_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account_index')
    success_message = _("Password updated!")
    email_warn_subject = "account/account_password_warn_subject.txt"
    email_warn_body = "account/account_password_warn_body.txt"

    def form_valid(self, form):
        # Email sent to the current address for notification
        subject_warn = render_to_string(
            template_name=self.email_warn_subject,
            context={},
            request=self.request
        )
        subject_warn = ''.join(subject_warn.splitlines())
        message_warn = render_to_string(
            template_name=self.email_warn_body,
            context={},
            request=self.request
        )

        self.request.user.email_user(subject_warn, message_warn, settings.DEFAULT_FROM_EMAIL)

        return super().form_valid(form)
