#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views import View
from django_otp import devices_for_user
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from ftl.otp_plugins.otp_ftl.models import Fido2Device


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class ListOTPDevice(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # Static token
        static_device = StaticDevice.objects.filter(user=user)

        # TOTP
        totp_device = TOTPDevice.objects.filter(user=user)

        # FIDO2
        fido2_device = Fido2Device.objects.filter(user=user)

        context = {
            'static_device': static_device,
            'totp_device': totp_device,
            'fido2_device': fido2_device,
            'ftl_account': {'name': request.user.get_username(),  # get_username now return email
                            'isSuperUser': request.user.is_superuser},
        }
        return render(request, 'otp_ftl/device_list.html', context)


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
