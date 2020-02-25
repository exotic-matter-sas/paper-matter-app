#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import django.dispatch

pre_ftl_processing = django.dispatch.Signal(providing_args=["document"])
