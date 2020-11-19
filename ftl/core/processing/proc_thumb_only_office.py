#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import logging
from tempfile import TemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from jose import jwt

from core.mimes import mimetype_to_ext
from core.processing.ftl_processing import FTLDocProcessingBase, atomic_ftl_doc_update
from core.serializers import FTLDocumentDetailsOnlyOfficeSerializer

logger = logging.getLogger(__name__)


class FTLThumbnailGenerationOnlyOffice(FTLDocProcessingBase):
    supported_documents_types = [
        "text/plain",
        "application/rtf",
        "text/rtf",
        "application/msword",
        "application/vnd.ms-excel",
        "application/excel",
        "application/vnd.ms-powerpoint",
        "application/mspowerpoint",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.presentation",
        "application/vnd.oasis.opendocument.spreadsheet",
    ]

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"
        self.enabled = getattr(settings, "FTL_ENABLE_ONLY_OFFICE", False)

    def process(self, ftl_doc, force):
        if self.enabled:
            doc_serial = FTLDocumentDetailsOnlyOfficeSerializer(ftl_doc)

            only_office_config = {
                "async": False,
                "filetype": mimetype_to_ext(ftl_doc.type)[1:],
                "key": str(ftl_doc.pid),
                "outputtype": "png",
                "title": "thumbnail",
                "thumbnail": {"first": True, "aspect": 2},
                "url": doc_serial.get_download_url_temp(ftl_doc),
            }

            sign = jwt.encode(
                only_office_config,
                getattr(settings, "FTL_ONLY_OFFICE_SECRET_KEY"),
                algorithm="HS256",
            )

            r = requests.post(
                f"{getattr(settings, 'FTL_ONLY_OFFICE_SERVER_URL')}/ConvertService.ashx",
                json=only_office_config,
                headers={
                    "Authorization": f"Bearer {sign}",
                    "Accept": "application/json",
                },
            )

            if r.status_code == 200 and "fileUrl" in r.json():
                thumb_url = r.json()["fileUrl"]

                with requests.get(thumb_url, stream=True) as r:
                    r.raise_for_status()

                    with TemporaryFile() as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)

                        atomic_ftl_doc_update(
                            ftl_doc.pid, {"thumbnail_binary": File(f, "thumb.png")}
                        )
        else:
            logger.warning(
                f"{self.log_prefix} OnlyOffice processing plugin enabled but FTL_ENABLE_ONLY_OFFICE is disabled"
            )
