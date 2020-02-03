#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.views.generic.base import ContextMixin
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice


class FTLUserContextDataMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ftl_account'] = {'name': self.request.user.get_username(),
                                  'isSuperUser': self.request.user.is_superuser,
                                  'otp_warning': any(
                                      [True for d in devices_for_user(self.request.user, confirmed=None) if
                                       (isinstance(d, StaticDevice) and not d.token_set.exists()) or not d.confirmed])
                                  }
        return context
