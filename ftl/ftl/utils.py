#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.


def initialize_static(cls):
    """
    Use as a decorator to simulate a static initializer (execute class method one time for the
    whole lifecycle of the class).
    :param cls:
    :return:
    """
    cls.init_static()
    return cls
