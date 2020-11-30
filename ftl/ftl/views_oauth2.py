#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django_otp.decorators import otp_required
from oauth2_provider import views


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationView(views.AuthorizationView):
    pass


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationCodeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ftl/oauth2_provider/authorization_code.html")


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationOKView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ftl/oauth2_provider/authorization_ok.html")


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationKOView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "ftl/oauth2_provider/authorization_ko.html")
