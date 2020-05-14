#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from pathlib import Path
from typing import Optional

import puremagic
from django.conf import settings

MIMETYPES_EXT_DICT = {}
EXTS = []

for ext, mimes in settings.FTL_SUPPORTED_DOCUMENTS_TYPES.items():
    _ext = ext.lower()

    EXTS.append(_ext)

    for mime in mimes:
        MIMETYPES_EXT_DICT[mime.lower()] = _ext


def mimetype_to_ext(mime: str) -> Optional[str]:
    if mime.lower() not in MIMETYPES_EXT_DICT:
        return None  # File is not supported
    return MIMETYPES_EXT_DICT[mime]


def guess_mimetype(buffer, filename: str = None) -> Optional[str]:
    try:
        return puremagic.from_string(buffer, mime=True, filename=filename)
    except puremagic.PureError:
        if filename and Path(filename).suffix in EXTS:
            return settings.FTL_SUPPORTED_DOCUMENTS_TYPES[
                Path(filename).suffix.lower()
            ][0]
