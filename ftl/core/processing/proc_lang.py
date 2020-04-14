#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import logging

from langid.langid import LanguageIdentifier, model

from core.processing.ftl_processing import FTLDocProcessingBase

logger = logging.getLogger(__name__)

"""
Convert langid lang code to PgSQL ts_vector lang code
List is limited to lang available on a PgSQL 11.5 setup (SELECT cfgname FROM pg_ts_config)
"""
COUNTRY_CODE_INDEX = {
    "da": "danish",
    "nl": "dutch",
    "en": "english",
    "fi": "finnish",
    "fr": "french",
    "de": "german",
    "hu": "hungarian",
    "it": "italian",
    "nb": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "es": "spanish",
    "sv": "swedish",
    "tr": "turkish",
}


class FTLLangDetectorLangId(FTLDocProcessingBase):
    supported_documents_types = ["*"]

    def __init__(self):
        self.log_prefix = f"[{self.__class__.__name__}]"
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        self.default_language = "simple"

    def process(self, ftl_doc, force):
        if force or not ftl_doc.language:
            detected_lang, confidence = self.identifier.classify(ftl_doc.content_text)
            if confidence > 0.5:
                try:
                    ftl_doc.language = COUNTRY_CODE_INDEX[detected_lang]
                # Lang not supported by PgSQL (see COUNTRY_CODE_INDEX)
                except KeyError:
                    logger.warning(
                        f"{self.log_prefix} {ftl_doc.pid} Lang {detected_lang} not registered as "
                        f'supported PgSQL lang, search will fallback to "simple" lang for this document'
                    )
                    ftl_doc.language = self.default_language
            else:
                logger.warning(
                    f"{self.log_prefix} {ftl_doc.pid} Lang detection confidence too low, search will"
                    f' fallback to "simple" lang for this document'
                )
                ftl_doc.language = self.default_language
            ftl_doc.save()
        else:
            logger.debug(
                f"{self.log_prefix} Skipping lang detection for document {ftl_doc.pid}"
            )
