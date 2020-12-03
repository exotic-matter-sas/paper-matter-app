#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from djproxy.views import HttpProxy


# This reverse proxy is forwarding all requests to /local/ to the dev NodeJS server. It's only active on DEBUG mode.
# Resolve most of the CORS issue, especially the one with PDF.js worker script.
class LocalProxy(HttpProxy):
    base_url = "http://localhost:8080/local/"
    proxy_middleware = ["ftl.view_local_proxy.LocalProxyAddHeader"]


# Just add a header to indicate the file is being served by the reverse proxy
class LocalProxyAddHeader:
    def process_response(self, proxy, request, upstream_response, response):
        response["X-From-Local-Node"] = True
        return response
