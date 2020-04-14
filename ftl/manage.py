#!/usr/bin/env python

#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ftl.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Security to avoid breaking FTL instance by mistake
    if "createsuperuser" in sys.argv:
        red_message = "\x1b[1;31m{}\033[0m"
        print(
            red_message.format(
                "WARNING: By creating a new superuser you could broke your Paper Matter instance, superuser "
                "should be created by initial setup. You should not have more then 1 superuser at any point"
            )
        )
        user_input = input("Do you wish to continue? (yes or no)\n")
        if user_input == "yes":
            pass
        else:
            print("createsuperuser command cancelled")
            exit()

    execute_from_command_line(sys.argv)
