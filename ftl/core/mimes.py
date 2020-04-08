#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import mimetypes
from typing import Optional

from django.conf import settings

MIMETYPES_EXT_DICT = {}

for ext in settings.FTL_SUPPORTED_DOCUMENTS_TYPES:
    mime, _ = mimetypes.guess_type(f"document{ext}")
    MIMETYPES_EXT_DICT[mime] = ext


def mimetype_to_ext(mime: str) -> Optional[str]:
    if mime not in MIMETYPES_EXT_DICT:
        return None  # File is not supported
    return MIMETYPES_EXT_DICT[mime]
