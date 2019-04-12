from djproxy.views import HttpProxy


# This reverse proxy is forwarding all requests to /local/ to the dev NodeJS server. It's only active on DEBUG mode.
# Resolve most of the CORS issue, especially the one with PDF.js worker script.
class LocalProxy(HttpProxy):
    base_url = 'http://localhost:8080/local/'
