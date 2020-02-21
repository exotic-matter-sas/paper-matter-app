#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views import View
from django.views.generic import DeleteView
from django_otp import devices_for_user
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from core.ftl_mixins import FTLUserContextDataMixin
from ftl.otp_plugins.otp_ftl.models import Fido2Device


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class ListOTPDevices(FTLUserContextDataMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # Static token
        static_devices = StaticDevice.objects.filter(user=user)

        # TOTP
        totp_devices = TOTPDevice.objects.filter(user=user)

        # FIDO2
        fido2_devices = Fido2Device.objects.filter(user=user)

        context_data = self.get_context_data()
        context_data.update({
            'static_devices': static_devices,
            'totp_devices': totp_devices,
            'fido2_devices': fido2_devices
        })

        return render(request, 'otp_ftl/device_list.html', context_data)


@method_decorator(login_required, name='dispatch')
class OTPCheckView(View):
    def get(self, request, *args, **kwargs):
        devices = list((d.persistent_id, d.name) for d in devices_for_user(request.user))
        _next = request.GET.get('next', None)
        if _next:
            request.session['next'] = _next

        if [d for d in devices if Fido2Device.model_label() in d[0]]:
            return redirect('otp_fido2_check', *args, **kwargs)

        if [d for d in devices if TOTPDevice.model_label() in d[0]]:
            return redirect('otp_totp_check', *args, **kwargs)

        if [d for d in devices if StaticDevice.model_label() in d[0]]:
            return redirect('otp_static_check', *args, **kwargs)


class FTLBaseCheckView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['have_fido2'] = Fido2Device.objects.filter(user=self.request.user, confirmed=True).exists()
        context['have_totp'] = TOTPDevice.objects.filter(user=self.request.user, confirmed=True).exists()
        context['have_static'] = StaticDevice.objects.filter(user=self.request.user, confirmed=True).exists()
        return context

    def get_success_url(self):
        url = self.request.session.get('next', None)
        if url:
            del self.request.session['next']
            url_is_safe = is_safe_url(
                url=url,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            return url if url_is_safe else self.success_url

        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        request.session['saved_expiration'] = request.session.get_expiry_age()
        request.session.set_expiry(600)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session.set_expiry(self.request.session.get('saved_expiration', settings.SESSION_COOKIE_AGE))
        return super().form_valid(form)


class FTLBaseDeleteView(FTLUserContextDataMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        have_fido2 = Fido2Device.objects.filter(user=self.request.user, confirmed=True)
        if self.model is Fido2Device:
            have_fido2 = have_fido2.exclude(pk=self.object.pk)
        have_fido2 = have_fido2.exists()

        have_totp = TOTPDevice.objects.filter(user=self.request.user, confirmed=True)
        if self.model is TOTPDevice:
            have_totp = have_totp.exclude(pk=self.object.pk)
        have_totp.exists()

        context['last_otp'] = not have_fido2 and not have_totp
        return context

    def delete(self, request, *args, **kwargs):
        delete = super().delete(request, *args, **kwargs)

        if self.get_context_data()['last_otp']:
            Fido2Device.objects.filter(user=self.request.user).delete()
            TOTPDevice.objects.filter(user=self.request.user).delete()
            StaticDevice.objects.filter(user=self.request.user).delete()

        return delete
