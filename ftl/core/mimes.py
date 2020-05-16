#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import os
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


def guess_mimetype(django_uploaded_file, filename: str = None) -> Optional[str]:
    try:
        head, foot = _uploaded_file_obj_to_buffer(django_uploaded_file)
        return puremagic.from_string(head + foot, mime=True, filename=filename)
    except puremagic.PureError:
        if filename and Path(filename).suffix in EXTS:
            return settings.FTL_SUPPORTED_DOCUMENTS_TYPES[
                Path(filename).suffix.lower()
            ][0]


def _uploaded_file_obj_to_buffer(
    django_file_obj, sample_size: int = 8096
) -> (bytes, bytes):
    """
    Optimize memory usage by only returning the first and last 8096 bytes (default).
    """
    head = django_file_obj.read(sample_size)
    try:
        # Try to position to the almost end of the file
        seek_pos = django_file_obj.seek(-sample_size, os.SEEK_END)
        if seek_pos == 0:  # The file was smaller that the sample size
            return head, b""
    except IOError:
        return head, b""

    # Continue reading from the end position found
    foot = django_file_obj.read()
    return head, foot
