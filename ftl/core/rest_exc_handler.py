#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code
        if isinstance(exc, APIException):
            response.data["code"] = exc.get_codes()

    return response
