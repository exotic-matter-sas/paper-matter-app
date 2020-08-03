#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.conf import settings
from django.conf.urls import url
from django_otp.decorators import otp_required
from oauth2_provider import views

app_name = "oauth2_provider"

urlpatterns = [
    # Token management views
    url(
        r"^authorized_tokens/$",
        otp_required(
            views.AuthorizedTokensListView.as_view(
                template_name="account/oauth2_authorized-tokens.html"
            ),
            if_configured=True,
        ),
        name="authorized-token-list",
    ),
    url(
        r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$",
        otp_required(
            views.AuthorizedTokenDeleteView.as_view(
                template_name="account/oauth2_authorized-token-delete.html"
            ),
            if_configured=True,
        ),
        name="authorized-token-delete",
    ),
]

# API Application management views
if getattr(settings, "FTL_ENABLE_DEV_API", False):
    urlpatterns = urlpatterns + [
        url(
            r"^applications/$",
            views.ApplicationList.as_view(
                template_name="account/oauth2_application_list.html"
            ),
            name="list",
        ),
        url(
            r"^applications/register/$",
            views.ApplicationRegistration.as_view(
                template_name="account/oauth2_application_registration_form.html"
            ),
            name="register",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/$",
            views.ApplicationDetail.as_view(
                template_name="account/oauth2_application_detail.html"
            ),
            name="detail",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/delete/$",
            views.ApplicationDelete.as_view(
                template_name="account/oauth2_application_confirm_delete.html"
            ),
            name="delete",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/update/$",
            views.ApplicationUpdate.as_view(
                template_name="account/oauth2_application_form.html"
            ),
            name="update",
        ),
    ]
