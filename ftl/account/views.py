from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, UpdateView

from account.forms import EmailUpdateForm


class AccountView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'ftl_account': {'name': request.user.get_username(),  # get_username now return email
                            'isSuperUser': request.user.is_superuser},
        }
        return render(request, 'account/account_index.html', context)


class AccountEmailView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "account/account_email.html"
    form_class = EmailUpdateForm
    success_url = reverse_lazy('account_index')
    success_message = "Email successfully updated "

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ftl_account'] = {'name': self.request.user.get_username(),
                                  'isSuperUser': self.request.user.is_superuser}
        return context

    def get_object(self, queryset=None):
        return self.request.user


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
