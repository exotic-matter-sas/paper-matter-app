#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import logging
from tempfile import TemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from jose import jwt

from core.mimes import mimetype_to_ext
from core.processing import ftl_processing
from core.processing.ftl_processing import FTLDocProcessingBase
from core.serializers import FTLDocumentDetailsOnlyOfficeSerializer

logger = logging.getLogger(__name__)


class FTLThumbnailGenerationOnlyOffice(FTLDocProcessingBase):
    supported_documents_types = getattr(
        settings, "FTL_ONLY_OFFICE_SUPPORTED_DOCUMENTS_TYPES", []
    )

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"
        self.enabled = getattr(settings, "FTL_ENABLE_ONLY_OFFICE", False)

    def process(self, ftl_doc, force):
        if self.enabled:
            if force or not ftl_doc.thumbnail_binary:
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

                if r.status_code == 200:
                    response_json = r.json()
                    if "fileUrl" in response_json:
                        thumb_url = response_json["fileUrl"]

                        with requests.get(thumb_url, stream=True) as r:
                            r.raise_for_status()

                            with TemporaryFile() as f:
                                for chunk in r.iter_content(chunk_size=1024):
                                    f.write(chunk)

                                ftl_processing.atomic_ftl_doc_update(
                                    ftl_doc.pid,
                                    {"thumbnail_binary": File(f, "thumb.png")},
                                )
                    else:
                        logger.error(
                            f"{self.log_prefix} An error occurred with OnlyOffice conversion server {response_json}"
                        )
        else:
            logger.warning(
                f"{self.log_prefix} OnlyOffice processing plugin enabled but FTL_ENABLE_ONLY_OFFICE is disabled"
            )
