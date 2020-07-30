#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.conf.urls import url
from django_otp.decorators import otp_required
from oauth2_provider import views

app_name = "oauth2_provider"

urlpatterns = [
    # Token management views
    url(
        r"^authorized_tokens/$",
        otp_required(views.AuthorizedTokensListView.as_view(), if_configured=True),
        name="authorized-token-list",
    ),
    url(
        r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$",
        otp_required(views.AuthorizedTokenDeleteView.as_view(), if_configured=True),
        name="authorized-token-delete",
    ),
    # API Application management views
    # url(r"^applications/$", views.ApplicationList.as_view(), name="list"),
    # url(
    #     r"^applications/register/$",
    #     views.ApplicationRegistration.as_view(),
    #     name="register",
    # ),
    # url(
    #     r"^applications/(?P<pk>[\w-]+)/$",
    #     views.ApplicationDetail.as_view(),
    #     name="detail",
    # ),
    # url(
    #     r"^applications/(?P<pk>[\w-]+)/delete/$",
    #     views.ApplicationDelete.as_view(),
    #     name="delete",
    # ),
    # url(
    #     r"^applications/(?P<pk>[\w-]+)/update/$",
    #     views.ApplicationUpdate.as_view(),
    #     name="update",
    # ),
]
