from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django_otp import devices_for_user


@method_decorator(login_required, name='dispatch')
class OTPCheckView(View):
    def get(self, request, *args, **kwargs):
        devices = list((d.persistent_id, d.name) for d in devices_for_user(request.user))

        if [d for d in devices if "otp_webauthn" in d[0]]:
            return redirect('otp_webauthn_check')

        if [d for d in devices if "otp_totp" in d[0]]:
            return redirect('otp_totp_check')

        if [d for d in devices if "otp_static" in d[0]]:
            return redirect('otp_static_check')
