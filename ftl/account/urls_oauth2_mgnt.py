#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
from django.conf import settings
from django.conf.urls import url
from django_otp.decorators import otp_required

from account import views_oauth2_mgnt

app_name = "oauth2_provider"

urlpatterns = [
    # Token management views
    url(
        r"^authorized_tokens/$",
        otp_required(
            views_oauth2_mgnt.FTLAccountAuthorizedTokensListView.as_view(
                template_name="account/oauth2_authorized-tokens.html"
            ),
            if_configured=True,
        ),
        name="authorized-token-list",
    ),
    url(
        r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$",
        otp_required(
            views_oauth2_mgnt.FTLAccountAuthorizedTokenDeleteView.as_view(
                template_name="account/oauth2_authorized-token-delete.html"
            ),
            if_configured=True,
        ),
        name="authorized-token-delete",
    ),
]

# API Application management views
if getattr(settings, "FTL_ENABLE_DEV_API", False):
    urlpatterns += [
        url(
            r"^applications/$",
            views_oauth2_mgnt.FTLAccountApplicationList.as_view(
                template_name="account/oauth2_application_list.html"
            ),
            name="list",
        ),
        url(
            r"^applications/register/$",
            views_oauth2_mgnt.FTLAccountApplicationRegistration.as_view(
                template_name="account/oauth2_application_registration_form.html"
            ),
            name="register",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/$",
            views_oauth2_mgnt.FTLAccountApplicationDetail.as_view(
                template_name="account/oauth2_application_detail.html"
            ),
            name="detail",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/delete/$",
            views_oauth2_mgnt.FTLAccountApplicationDelete.as_view(
                template_name="account/oauth2_application_confirm_delete.html"
            ),
            name="delete",
        ),
        url(
            r"^applications/(?P<pk>[\w-]+)/update/$",
            views_oauth2_mgnt.FTLAccountApplicationUpdate.as_view(
                template_name="account/oauth2_application_form.html"
            ),
            name="update",
        ),
    ]
