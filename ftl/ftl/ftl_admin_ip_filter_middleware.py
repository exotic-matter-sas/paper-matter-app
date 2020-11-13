#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import ipaddress

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import Http404
from ipware import get_client_ip


class FTLAdminIPFilter:
    def __init__(self, get_response):
        if not getattr(settings, "FTL_ADMIN_ENABLE_IP_PROTECTION", False):
            raise MiddlewareNotUsed()

        self.get_response = get_response
        self.ips = getattr(settings, "FTL_ADMIN_IP_RANGE_ALLOWED", [])
        self.proxy_count = getattr(settings, "FTL_ADMIN_IP_PROXY_COUNT", None)
        self.metas = getattr(settings, "FTL_ADMIN_IP_META_PRECEDENCE_ORDER", None)

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        # This code must be after the response because "app_name" is only resolved after the view is generated
        if request.resolver_match and request.resolver_match.app_name == "admin":
            if self.is_blocked(request):
                raise Http404()

        return response

    def is_blocked(self, request):
        # Handle reverse proxy and header name for IP (useful for load-balancer)
        client_ip, _ = get_client_ip(
            request, proxy_count=self.proxy_count, proxy_order=self.metas
        )

        if not client_ip:
            return True

        for ip_range in self.ips:
            if ipaddress.ip_address(client_ip) in ipaddress.ip_network(ip_range):
                return False

        return True
