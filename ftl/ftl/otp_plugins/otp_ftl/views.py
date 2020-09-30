#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views import View
from django.views.generic import DeleteView
from django.views.generic.base import ContextMixin
from django_otp import devices_for_user
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from core.ftl_account_processors_mixin import FTLAccountProcessorMixin
from ftl.otp_plugins.otp_ftl.models import Fido2Device
from ftl.views_auth import LoginViewFTL


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class ListOTPDevices(FTLAccountProcessorMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # Static token
        static_devices = StaticDevice.objects.filter(user=user)

        # TOTP
        totp_devices = TOTPDevice.objects.filter(user=user)

        # FIDO2
        fido2_devices = Fido2Device.objects.filter(user=user)

        context_data = self.get_context_data_with_request(request)
        context_data.update(
            {
                "static_devices": static_devices,
                "totp_devices": totp_devices,
                "fido2_devices": fido2_devices,
            }
        )

        return render(request, "otp_ftl/device_list.html", context_data)


@method_decorator(login_required, name="dispatch")
class OTPCheckView(View):
    def get(self, request, *args, **kwargs):
        # Reduce session expiration to 10 minutes during 2FA check (in case user afk).
        request.session.set_expiry(600)

        devices = list(
            (d.persistent_id, d.name) for d in devices_for_user(request.user)
        )
        _next = request.GET.get("next", None)
        if _next:
            request.session["next"] = _next

        # Redirect to available device check page, from most secure to less secure one
        if [d for d in devices if Fido2Device.model_label() in d[0]]:
            return redirect("otp_fido2_check", *args, **kwargs)

        if [d for d in devices if TOTPDevice.model_label() in d[0]]:
            return redirect("otp_totp_check", *args, **kwargs)

        if [d for d in devices if StaticDevice.model_label() in d[0]]:
            return redirect("otp_static_check", *args, **kwargs)


class FTLBaseCheckView(LoginViewFTL):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["have_fido2"] = Fido2Device.objects.filter(
            user=self.request.user, confirmed=True
        ).exists()
        context["have_totp"] = TOTPDevice.objects.filter(
            user=self.request.user, confirmed=True
        ).exists()
        context["have_static"] = StaticToken.objects.filter(
            device__user=self.request.user
        ).exists()
        return context

    def get_success_url(self):
        url = self.request.session.get("next", None)
        if url:
            del self.request.session["next"]
            url_is_safe = is_safe_url(
                url=url,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            return url if url_is_safe else self.success_url

        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Restore session expiration to default value
        self.request.session.set_expiry(None)
        return super().form_valid(form)


class FTLBaseDeleteView(DeleteView):
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

        context["last_otp"] = not have_fido2 and not have_totp
        return context

    def delete(self, request, *args, **kwargs):
        delete = super().delete(request, *args, **kwargs)

        if self.get_context_data()["last_otp"]:
            Fido2Device.objects.filter(user=self.request.user).delete()
            TOTPDevice.objects.filter(user=self.request.user).delete()
            StaticDevice.objects.filter(user=self.request.user).delete()

        return delete
