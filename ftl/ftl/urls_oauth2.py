#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django.conf.urls import url
from oauth2_provider import views

from ftl import views_oauth2

urlpatterns = [
    url(r"^authorize/$", views_oauth2.FTLAuthorizationView.as_view(), name="authorize"),
    url(r"^token/$", views.TokenView.as_view(), name="token"),
    url(r"^revoke_token/$", views.RevokeTokenView.as_view(), name="revoke-token"),
    # url(r"^introspect/$", views.IntrospectTokenView.as_view(), name="introspect"),
]
