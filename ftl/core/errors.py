#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.utils.translation import gettext_lazy as _


def get_api_error(code):
    return {
        'code': code,
        'details': ERROR_CODES_DETAILS[code]
    }


ERROR_CODES_DETAILS = {
    'folder_name_unique_for_org_level': _('A folder with this name already exist'),
    'folder_parent_invalid': _('A folder can\'t be move inside one of its children'),
    'ftl_folder_not_found': _('Specified ftl_folder doesn\'t exist'),
    'ftl_document_md5_mismatch': _('Document have been corrupted during upload, please retry')
}


class PluginUnsupportedStorage(Exception):
    pass
