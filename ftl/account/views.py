from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from account.forms import EmailSendForm


class AccountView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'ftl_account': {'name': request.user.get_username(),  # get_username now return email
                            'isSuperUser': request.user.is_superuser},
        }
        return render(request, 'account/account_index.html', context)


class AccountEmailChangeView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "account/account_email.html"
    email_change_subject = "account/account_email_change_subject.txt"
    email_change_body = "account/account_email_change_body.txt"
    form_class = EmailSendForm
    success_url = reverse_lazy('account_index')
    success_message = "A confirmation email has been sent to your new email."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ftl_account'] = {'name': self.request.user.get_username(),
                                  'isSuperUser': self.request.user.is_superuser}
        return context

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

        activation_key = signing.dumps(
            obj=email_,
            salt='email_change'
        )

        subject = render_to_string(
            template_name=self.email_change_subject,
            context=self.get_email_context(activation_key),
            request=self.request
        )

        subject = ''.join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_change_body,
            context=self.get_email_context(activation_key),
            request=self.request
        )

        send_mail(subject, message, None, [email_])

        return super().form_valid(form)


class AccountEmailChangeValidateView(LoginRequiredMixin, View):
    success_message = "Email successfully updated"

    def get(self, request, *args, **kwargs):
        if 'token' in kwargs:
            email = signing.loads(
                kwargs['token'],
                salt='email_change',
                max_age=timedelta(minutes=10)
            )

            user = self.request.user
            user.email = email
            user.save()

            messages.success(self.request, self.success_message)

        return HttpResponseRedirect(reverse_lazy('account_index'))


class AccountPasswordView(LoginRequiredMixin, FormView):
    template_name = "account/account_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account_index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ftl_account'] = {'name': self.request.user.get_username(),
                                  'isSuperUser': self.request.user.is_superuser}
        return context
