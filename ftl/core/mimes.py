#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import mimetypes
from typing import Optional

from django.conf import settings

MIMETYPES = {}

for ext in settings.FTL_SUPPORTED_FILETYPES:
    mime, _ = mimetypes.guess_type(f"document{ext}")
    MIMETYPES[mime] = ext


def mimetype_to_ext(mime: str) -> Optional[str]:
    if mime not in MIMETYPES:
        return None  # File is not supported
    return MIMETYPES[mime]
