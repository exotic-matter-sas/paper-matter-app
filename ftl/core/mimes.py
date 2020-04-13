#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import mimetypes
from typing import Optional

from django.conf import settings

MIMETYPES_EXT_DICT = {}
MIMETYPES_OVERRIDE = {
    ".rtf": "application/rtf"
}  # to get the same mimetypes when running Python on different OS

for ext in set(settings.FTL_SUPPORTED_DOCUMENTS_TYPES):
    _ext = ext.lower()
    if _ext in MIMETYPES_OVERRIDE:
        mime = MIMETYPES_OVERRIDE[_ext]
    else:
        mime, _ = mimetypes.guess_type(f"document{_ext}")

    MIMETYPES_EXT_DICT[mime.lower()] = _ext


def mimetype_to_ext(mime: str) -> Optional[str]:
    if mime.lower() not in MIMETYPES_EXT_DICT:
        return None  # File is not supported
    return MIMETYPES_EXT_DICT[mime]
