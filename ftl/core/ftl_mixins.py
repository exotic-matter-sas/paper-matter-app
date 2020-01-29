#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.views.generic.base import ContextMixin


class FTLUserContextDataMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ftl_account'] = {'name': self.request.user.get_username(),
                                  'isSuperUser': self.request.user.is_superuser}
        return context
