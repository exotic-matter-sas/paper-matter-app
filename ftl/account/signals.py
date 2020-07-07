#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import django.dispatch

pre_account_disable = django.dispatch.Signal(providing_args=["org"])
post_account_disable = django.dispatch.Signal(providing_args=["org"])
