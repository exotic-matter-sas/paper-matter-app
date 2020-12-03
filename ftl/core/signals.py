#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import django.dispatch

pre_ftl_processing = django.dispatch.Signal(providing_args=["document"])
