#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

APP_NAME = "Paper Matter"

ADMIN1_EMAIL = "admin@localhost.com"
ADMIN1_PASS = "a123456!a"

ADMIN2_EMAIL = "admin2@localhost.com"
ADMIN2_PASS = "a123456!b"

ORG_NAME_1 = "Exotic Matter"
ORG_SLUG_1 = "exotic-matter"
ORG_NAME_2 = "Mozilla"
ORG_SLUG_2 = "mozilla"
ORG_NAME_3 = "Space Y"
ORG_SLUG_3 = "space-y"
ORG_NAME_4 = "Pear"
ORG_SLUG_4 = "pear"

USER1_EMAIL = "user1@localhost.com"
USER1_PASS = "a123456!1"

USER2_EMAIL = "user2@localhost.com"
USER2_PASS = "a123456!2"

USER3_EMAIL = "user3@localhost.com"
USER3_PASS = "a123456!3"

DOCUMENT1_TITLE = "test"
DOCUMENT1_NOTE = "Document 1 note"
DOCUMENT1_BINARY_PATH = "ftests/tools/test_documents/test.pdf"
DOCUMENT1_CONTENT = "Document 1 content"
DOCUMENT1_LANGUAGE = "english"

DOCUMENT2_TITLE = "Document 2"
DOCUMENT2_NOTE = "Document 2 note"
DOCUMENT2_CONTENT = "Document 2 content"

DOCUMENT_DOCX_TITLE = "Document DOCX"
DOCUMENT_DOCX_NOTE = "Document DOCX note"
DOCUMENT_DOCX_CONTENT = "Document DOCX content"
DOCUMENT_DOCX_BINARY_PATH = "ftests/tools/test_documents/word.docx"

FOLDER1_NAME = "Folder 1"
FOLDER2_NAME = "Folder 2"
FOLDER3_NAME = "Folder 3"


DOCUMENT_SHARING_LINK_1_NOTE = "Document sharing link 1 note"
DOCUMENT_SHARING_LINK_1_PASS = "dsl123"

STATIC_DEVICE_NAME = "My emergency codes"
STATIC_DEVICE_CODES_LIST = [
    "SD1",
    "SD2",
    "SD3",
    "SD4",
    "SD5",
    "SD6",
    "SD7",
    "SD8",
    "SD9",
    "SD10",
]

TOTP_DEVICE_NAME = "My smartphone"
TOTP_DEVICE_SECRET_TIME = 1582109713.4242425
TOTP_DEVICE_SECRET_KEY = "f679758a45fa55cd14b583c8505bf4d12eb76f27"
TOTP_DEVICE_VALID_TOKEN = (
    "954370"  # value get from TOTP.token() in debug mode with the 2 settings above
)
TOTP_DEVICE_INVALID_TOKEN = "123456"

FIDO2_DEVICE_NAME = "My security key"
