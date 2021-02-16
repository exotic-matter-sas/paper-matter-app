#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
from oauth2_provider.views import (
    AuthorizedTokensListView,
    AuthorizedTokenDeleteView,
    ApplicationList,
    ApplicationRegistration,
    ApplicationDetail,
    ApplicationDelete,
    ApplicationUpdate,
)

from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin


class FTLAccountAuthorizedTokensListView(
    FTLAccountProcessorContextMixin, AuthorizedTokensListView
):
    pass


class FTLAccountAuthorizedTokenDeleteView(
    FTLAccountProcessorContextMixin, AuthorizedTokenDeleteView
):
    pass


class FTLAccountApplicationList(FTLAccountProcessorContextMixin, ApplicationList):
    pass


class FTLAccountApplicationRegistration(
    FTLAccountProcessorContextMixin, ApplicationRegistration
):
    pass


class FTLAccountApplicationDetail(FTLAccountProcessorContextMixin, ApplicationDetail):
    pass


class FTLAccountApplicationDelete(FTLAccountProcessorContextMixin, ApplicationDelete):
    pass


class FTLAccountApplicationUpdate(FTLAccountProcessorContextMixin, ApplicationUpdate):
    pass
