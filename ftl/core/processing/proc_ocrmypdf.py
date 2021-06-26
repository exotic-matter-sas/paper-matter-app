#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import time
from datetime import timedelta, datetime

import requests
from django.conf import settings

from core.processing.ftl_processing import FTLOCRBase
from ftl.enums import FTLStorages


class FTLOCRmyPDF(FTLOCRBase):
    supported_documents_types = ["application/pdf"]

    def __init__(
        self,
        api_url=settings.FTL_OCRMYPDF_API_URL,
        api_key=settings.FTL_OCRMYPDF_API_KEY,
    ):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.supported_storages = [
            FTLStorages.FILE_SYSTEM,
            FTLStorages.GCS,
            FTLStorages.AWS_S3,
        ]
        self.timeout = timedelta(minutes=5)

    def _extract_text(self, ftl_doc_binary):
        params = {"lang": ["eng", "fra"]}
        files = {"file": ftl_doc_binary}

        rp = requests.post(
            f"{self.api_url}/ocr",
            params=params,
            files=files,
            headers={"X-API-KEY": self.api_key},
        )

        rp.raise_for_status()
        pid = rp.json()["pid"]

        rg = requests.get(
            f"{self.api_url}/ocr/{pid}", headers={"X-API-KEY": self.api_key}
        )
        rg.raise_for_status()

        expire = datetime.now() + self.timeout
        while rg.json()["status"] != "done" and datetime.now() < expire:
            time.sleep(5)
            rg = requests.get(
                f"{self.api_url}/ocr/{pid}", headers={"X-API-KEY": self.api_key}
            )
            rg.raise_for_status()

        if rg.json()["status"] == "done":
            rt = requests.get(
                f"{self.api_url}/ocr/{pid}/txt", headers={"X-API-KEY": self.api_key}
            )
            rt.raise_for_status()
            return rt.content

        return None
