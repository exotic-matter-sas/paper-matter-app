#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.contrib import messages
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.utils.translation import gettext as _


def show_message(request, **kwargs):
    if "auto" in request.GET:
        messages.warning(
            request,
            _("Your session has expired or have been invalidated. Please log back in."),
        )
    else:
        messages.success(request, _("You have been logged out. See you!"))


user_logged_out.connect(show_message, dispatch_uid="login_page")


def set_ftl_session(request, **kwargs):
    org = kwargs["user"].org
    request.session["org_id"] = org.id
    request.session["org_name"] = org.name


user_logged_in.connect(set_ftl_session, dispatch_uid="set_ftl_session")
