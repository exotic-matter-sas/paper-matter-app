#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import rest_framework
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response:
        # Handle a rare case where response.data will be a list object
        # instead of a dict because a ValidationError was raised
        if isinstance(exc, rest_framework.exceptions.ValidationError):
            details = {"detail": exc.get_full_details()}
            response.data = details

        response.data["status_code"] = getattr(response, "status_code", 500)

        if isinstance(exc, APIException):
            response.data["code"] = getattr(exc, "default_code", "none")

    return response
